#![no_std]
use core::ffi::c_void;

use threadx_sys::_tx_initialize_kernel_enter;

pub mod allocator;
pub mod error;
pub mod event_flags;
pub mod executor;
pub mod mutex;
pub mod pool;
pub mod queue;
pub mod semaphore;
pub mod thread;
pub mod time;
pub mod timer;
pub mod select;

pub use threadx_sys::__tx_PendSVHandler as tx_pendsv_handler;
pub use threadx_sys::_tx_timer_interrupt as tx_timer_interrupt;

pub use either;
/// Initialize ThreadX

/// This callback is called by threadx for low level initialization.
/// The callback should return a slice of memory that is available for the application to use.
/// Note that this is a function and not a closure. This means that the callback cannot capture
/// any variables. The input to this callback is the number of ticks per second that is
/// expected by the build configuration of threadx
pub type LowLevelInitCb = fn(ticks_per_second: u32);
/// This callback is called by threadx for the definition of the Application. All application
/// resources are created in this callback. The input to this callback is the memory that can
/// be used as heap memory.
/// Note that this is a function and not a closure. This means that the callback cannot capture
/// any variables.
/// If you need to create data structures that are needed by other parts of your
/// code, you must store them in static variables.
///
/// It is conventional in Threadx to create all your applications resources here and then start
/// the threads that are part of your application.

pub type AppDefineCb = fn(*mut u8);

pub struct Builder {
    low_level_init_cb: LowLevelInitCb,
    app_define_cb: AppDefineCb,
}
// TODO: Remove static mut 
static mut INIT_CB: Option<LowLevelInitCb> = None;
static mut DEFINE_CB: Option<AppDefineCb> = None;

impl Builder {
    pub fn new(low_level_init_cb: LowLevelInitCb, app_define_cb: AppDefineCb) -> Self {
        Builder {
            low_level_init_cb,
            app_define_cb,
        }
    }

    /// Initialize ThreadX
    /// The low level init callback is called first. This allows the application to perform
    /// low level initialization such as setting up the heap and initializing the interrupt
    /// priorities as needed by the hardware platform. The `app_define_cb` is called next. This
    /// callback is where the application is defined.
    /// This function then initializes the ThreadX kernel and starts the application threads
    /// that were defined in the ``app_define_cb``. This function does not return.
    pub fn initialize(self) {
        //Safety:  The callbacks are called only after we call _tx_initialize_kernel_enter.  We call this
        // at the end of this function so we ensure that the callbacks are not called before we are ready.
        unsafe { INIT_CB = Some(self.low_level_init_cb) };
        //Safety:  The callbacks are called only after we call _tx_initialize_kernel_enter.  We call this
        // at the end of this function so we ensure that the callbacks are not called before we are ready.
        unsafe { DEFINE_CB = Some(self.app_define_cb) };

        unsafe { _tx_initialize_kernel_enter() };
        defmt::error!("ThreadX kernel should never return from _tx_initialize_kernel_enter");
    }
}

// This variable is defined by threadx and is used to store a pointer to the unused memory
unsafe extern "C" {
    static mut _tx_initialize_unused_memory: *mut c_void;
    // Defined in the cortex m crate in the linker script.
    static __sheap: *const c_void;

}

/// This function is called by threadx for low level initialization
/// such as setting up the heap and initializing the interrupt priorities
#[unsafe(no_mangle)]
unsafe extern "C" fn _tx_initialize_low_level() {
    // call the low level initialization callback. This callback returns the memory that
    // is available for the application to use.
    // Safety: This callback is called only after we initialize the INIT_CB in the initialize function
    // and it can never be `None`
    unsafe {
        INIT_CB.unwrap()(threadx_sys::TX_TIMER_TICKS_PER_SECOND);
        _tx_initialize_unused_memory = (&raw const __sheap).add(1) as *mut c_void;
    }
}

#[unsafe(no_mangle)]
unsafe extern "C" fn tx_application_define(mem_start: *mut c_void) {
    // Call the application definition callback
    // Safety: This callback is called only after we initialize the DEFINE_CB in the initialize function
    // and it can never be `None`
    // The kernel is started after this callback returns.
    unsafe {
        DEFINE_CB.unwrap()(mem_start as *mut u8);
    }
}
#[macro_export]
macro_rules! tx_checked_call_no_log {
    ($func:ident($($arg:expr),*)) => {
        {
            let ret = unsafe { $func($($arg),*) };
            if ret != threadx_sys::TX_SUCCESS {
                crate::error::TxResult::Err(TxError::from_u32(ret).unwrap_or(TxError::Unknown))
            } else {
                crate::error::TxResult::Ok(())
            }
        }
    }
}

#[macro_export]
macro_rules! tx_checked_call {
    ($func:ident($($arg:expr),*)) => {
        {
            use defmt::error;
            use defmt::trace;
            let ret = unsafe { $func($($arg),*) };
            if ret != threadx_sys::TX_SUCCESS {

                error!("ThreadX call {} returned {}", stringify!($func), ret);
                crate::error::TxResult::Err(TxError::from_u32(ret).unwrap_or(TxError::Unknown))
            } else {
                trace!("ThreadX call {} Success", stringify!($func));
                crate::error::TxResult::Ok(())
            }
        }
    }
}

#[repr(u32)]
pub enum WaitOption {
    WaitForever = threadx_sys::TX_WAIT_FOREVER,
    NoWait = threadx_sys::TX_NO_WAIT,
}
