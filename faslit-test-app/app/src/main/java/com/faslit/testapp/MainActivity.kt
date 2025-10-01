package com.faslit.testapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import org.eclipse.paho.client.mqttv3.*
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity() {
    private val viewModel: FASLitViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize MQTT connection
        viewModel.connect()

        setContent {
            FASLitTestAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    FASLitScreen(viewModel)
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        viewModel.disconnect()
    }
}

@Composable
fun FASLitTestAppTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFF6200EE),
            secondary = Color(0xFF03DAC6),
            background = Color(0xFF121212),
            surface = Color(0xFF1E1E1E)
        ),
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FASLitScreen(viewModel: FASLitViewModel) {
    val connectionStatus by viewModel.connectionStatus.collectAsState()
    val messages by viewModel.messages.collectAsState()
    val vehicleState by viewModel.vehicleState.collectAsState()

    val listState = rememberLazyListState()

    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("FASLit Test Monitor") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFF1E1E1E),
                    titleContentColor = Color.White
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Connection Status
            ConnectionStatusCard(connectionStatus)

            // Map View
            MapView(vehicleState)

            // Vehicle State Summary
            VehicleStateCard(vehicleState)

            // Messages List
            Text(
                "Live Messages",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(16.dp, 8.dp)
            )

            LazyColumn(
                state = listState,
                modifier = Modifier
                    .fillMaxSize()
                    .padding(horizontal = 8.dp),
                contentPadding = PaddingValues(bottom = 16.dp)
            ) {
                items(messages) { message ->
                    MessageCard(message)
                }
            }
        }
    }
}

// Coordinate conversion: CARLA to GPS (Berlin-centered)
// Berlin center: 52.5200° N, 13.4050° E
// CARLA (0, 0) maps to Berlin center
// Scale: 1 CARLA unit ≈ 0.00001 degrees (~1.1 meters at Berlin latitude)
fun carlaToGPS(carlaX: Float, carlaY: Float): LatLng {
    val berlinLat = 52.5200
    val berlinLng = 13.4050
    val scale = 0.00001 // 1 unit = ~1.1 meters

    // CARLA Y = North/South, X = East/West
    val lat = berlinLat + (carlaY * scale)
    val lng = berlinLng + (carlaX * scale)

    return LatLng(lat, lng)
}

@Composable
fun MapView(state: VehicleState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
            .padding(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E))
    ) {
        Column {
            Text(
                "Vehicle Map - Berlin, Germany",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                modifier = Modifier.padding(12.dp, 12.dp, 12.dp, 4.dp)
            )

            // Convert CARLA coordinates to GPS
            val vehiclePosition = carlaToGPS(state.location.x, state.location.y)
            val homePosition = carlaToGPS(1000f, 1000f) // Home at CARLA (1000, 1000)

            // Camera position - follow vehicle or center on home
            val cameraPosition = rememberCameraPositionState {
                position = CameraPosition.fromLatLngZoom(vehiclePosition, 14f)
            }

            // Update camera when vehicle moves
            LaunchedEffect(vehiclePosition) {
                cameraPosition.position = CameraPosition.fromLatLngZoom(vehiclePosition, 14f)
            }

            GoogleMap(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(8.dp),
                cameraPositionState = cameraPosition,
                properties = MapProperties(
                    mapType = MapType.NORMAL,
                    isMyLocationEnabled = false
                ),
                uiSettings = MapUiSettings(
                    zoomControlsEnabled = true,
                    compassEnabled = true,
                    myLocationButtonEnabled = false
                )
            ) {
                // Vehicle marker (blue car)
                Marker(
                    state = MarkerState(position = vehiclePosition),
                    title = "Vehicle",
                    snippet = "Location: (${state.location.x.toInt()}, ${state.location.y.toInt()})\nMode: ${state.autonomousMode}",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_BLUE)
                )

                // Home marker (green)
                Marker(
                    state = MarkerState(position = homePosition),
                    title = "Home",
                    snippet = "Destination",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN)
                )

                // Draw path between vehicle and home
                Polyline(
                    points = listOf(vehiclePosition, homePosition),
                    color = Color(0xFF03DAC6),
                    width = 5f
                )
            }
        }
    }
}

@Composable
fun ConnectionStatusCard(status: ConnectionStatus) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (status) {
                ConnectionStatus.CONNECTED -> Color(0xFF1B5E20)
                ConnectionStatus.CONNECTING -> Color(0xFFE65100)
                ConnectionStatus.DISCONNECTED -> Color(0xFFB71C1C)
            }
        )
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "● ",
                style = MaterialTheme.typography.headlineMedium,
                color = Color.White
            )
            Column {
                Text(
                    text = "MQTT Status",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.White.copy(alpha = 0.7f)
                )
                Text(
                    text = status.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
        }
    }
}

@Composable
fun VehicleStateCard(state: VehicleState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Vehicle State",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StateItem("Location", "${state.location.x}, ${state.location.y}")
                StateItem("Mode", state.autonomousMode)
            }
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StateItem("Passenger", if (state.passengerInVehicle) "In Vehicle" else "Not In Vehicle")
                StateItem("ETA", "${state.etaMinutes} min")
            }
        }
    }
}

@Composable
fun StateItem(label: String, value: String) {
    Column {
        Text(
            label,
            style = MaterialTheme.typography.bodySmall,
            color = Color.Gray
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            color = Color.White,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun MessageCard(message: FASLitMessage) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (message.type) {
                MessageType.HAZARD -> Color(0xFFD32F2F)
                MessageType.REROUTE -> Color(0xFFF57C00)
                MessageType.ALTERNATIVE -> Color(0xFF1976D2)
                MessageType.AUTONOMOUS -> Color(0xFF388E3C)
                MessageType.STATUS -> Color(0xFF424242)
                MessageType.SCREEN_COMMAND -> Color(0xFF7B1FA2)
                MessageType.OTHER -> Color(0xFF616161)
            }
        )
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    message.type.name,
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    message.timestamp,
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.White.copy(alpha = 0.7f)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                message.title,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
            if (message.description.isNotEmpty()) {
                Text(
                    message.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.White.copy(alpha = 0.9f)
                )
            }
        }
    }
}

enum class ConnectionStatus {
    CONNECTED, CONNECTING, DISCONNECTED
}

enum class MessageType {
    HAZARD, REROUTE, ALTERNATIVE, AUTONOMOUS, STATUS, SCREEN_COMMAND, OTHER
}

data class VehicleState(
    val location: Location = Location(),
    val autonomousMode: String = "N/A",
    val passengerInVehicle: Boolean = false,
    val etaMinutes: Int = 0
)

data class Location(
    val x: Float = 0f,
    val y: Float = 0f
)

data class FASLitMessage(
    val type: MessageType,
    val title: String,
    val description: String,
    val timestamp: String
)

class FASLitViewModel : ViewModel() {
    // MQTT Configuration - Update with your broker IP
    private val BROKER_URL = "tcp://192.168.41.250:1883" // Change to your broker IP
    private val CLIENT_ID = "FASLitTestApp-${UUID.randomUUID()}"

    private val TOPICS = arrayOf(
        "infotainment/hazard",
        "infotainment/reroute",
        "infotainment/alternatives",
        "infotainment/autonomous",
        "infotainment/status",
        "infotainment/screen_command"
    )

    private var mqttClient: MqttClient? = null
    private val dateFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    private val _connectionStatus = MutableStateFlow(ConnectionStatus.DISCONNECTED)
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatus

    private val _messages = MutableStateFlow<List<FASLitMessage>>(emptyList())
    val messages: StateFlow<List<FASLitMessage>> = _messages

    private val _vehicleState = MutableStateFlow(VehicleState())
    val vehicleState: StateFlow<VehicleState> = _vehicleState

    fun connect() {
        viewModelScope.launch {
            try {
                _connectionStatus.value = ConnectionStatus.CONNECTING

                mqttClient = MqttClient(BROKER_URL, CLIENT_ID, MemoryPersistence())

                val options = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 10
                    keepAliveInterval = 60
                    isAutomaticReconnect = true
                }

                mqttClient?.setCallback(object : MqttCallback {
                    override fun connectionLost(cause: Throwable?) {
                        _connectionStatus.value = ConnectionStatus.DISCONNECTED
                        addMessage(MessageType.OTHER, "Connection Lost", cause?.message ?: "Unknown error")
                    }

                    override fun messageArrived(topic: String?, message: MqttMessage?) {
                        message?.let {
                            val payload = String(it.payload)
                            handleMessage(topic ?: "unknown", payload)
                        }
                    }

                    override fun deliveryComplete(token: IMqttDeliveryToken?) {}
                })

                mqttClient?.connect(options)

                // Subscribe to all topics
                TOPICS.forEach { topic ->
                    mqttClient?.subscribe(topic, 1)
                }

                _connectionStatus.value = ConnectionStatus.CONNECTED
                addMessage(MessageType.OTHER, "Connected", "Successfully connected to MQTT broker")

            } catch (e: Exception) {
                _connectionStatus.value = ConnectionStatus.DISCONNECTED
                addMessage(MessageType.OTHER, "Connection Error", e.message ?: "Failed to connect")
            }
        }
    }

    fun disconnect() {
        try {
            mqttClient?.disconnect()
            mqttClient?.close()
            _connectionStatus.value = ConnectionStatus.DISCONNECTED
        } catch (e: Exception) {
            // Ignore disconnect errors
        }
    }

    private fun handleMessage(topic: String, payload: String) {
        try {
            val json = JSONObject(payload)
            val messageType = json.optString("message_type", "unknown")

            when (messageType) {
                "hazard_notification" -> {
                    val title = json.optString("title", "Hazard Alert")
                    val description = json.optString("description", "")
                    val severity = json.optString("severity", "medium")
                    addMessage(MessageType.HAZARD, title, "$description (Severity: $severity)")
                }
                "reroute_notification" -> {
                    val title = json.optString("title", "Route Updated")
                    val oldEta = json.optInt("old_eta_minutes", 0)
                    val newEta = json.optInt("new_eta_minutes", 0)
                    val timeSaved = json.optInt("time_saved_minutes", 0)
                    addMessage(MessageType.REROUTE, title, "Old: ${oldEta}min → New: ${newEta}min (Saved: ${timeSaved}min)")

                    _vehicleState.value = _vehicleState.value.copy(etaMinutes = newEta)
                }
                "alternative_suggestion" -> {
                    val title = json.optString("title", "Alternatives Available")
                    val alternatives = json.optJSONArray("alternatives")
                    val count = alternatives?.length() ?: 0
                    addMessage(MessageType.ALTERNATIVE, title, "$count alternative options available")
                }
                "autonomous_confirmation" -> {
                    val title = json.optString("title", "Autonomous Mode")
                    val mode = json.optString("autonomous_mode", "unknown")
                    addMessage(MessageType.AUTONOMOUS, title, "Mode: $mode")

                    _vehicleState.value = _vehicleState.value.copy(autonomousMode = mode)
                }
                "screen_command" -> {
                    val screenState = json.optString("screen_state", "MODES")
                    addMessage(MessageType.SCREEN_COMMAND, "Screen Command", "Switch to: $screenState")
                }
                "vehicle_status" -> {
                    // Update vehicle state
                    // current_location is sent as a JSON array [x, y, z]
                    val locationArray = json.optJSONArray("current_location")
                    val x = locationArray?.optDouble(0, 0.0)?.toFloat() ?: 0f
                    val y = locationArray?.optDouble(1, 0.0)?.toFloat() ?: 0f

                    val mode = if (json.optBoolean("autonomous_active", false)) "autonomous" else "manual"
                    val passengerIn = json.optBoolean("has_passenger", false)

                    // Calculate simple ETA (distance / speed assumption)
                    val speed = json.optDouble("current_speed", 50.0) // km/h
                    val destArray = json.optJSONArray("destination")
                    val destX = destArray?.optDouble(0, 1000.0)?.toFloat() ?: 1000f
                    val destY = destArray?.optDouble(1, 1000.0)?.toFloat() ?: 1000f

                    val distance = kotlin.math.sqrt(
                        ((destX - x) * (destX - x) + (destY - y) * (destY - y)).toDouble()
                    )
                    val etaMinutes = if (speed > 0) (distance / speed * 60).toInt() else 0

                    _vehicleState.value = VehicleState(
                        location = Location(x, y),
                        autonomousMode = mode,
                        passengerInVehicle = passengerIn,
                        etaMinutes = etaMinutes
                    )

                    // Don't add a message for every status update (too frequent)
                    // addMessage(MessageType.STATUS, "Vehicle Update", "Location: ($x, $y)")
                }
                else -> {
                    addMessage(MessageType.OTHER, "Unknown Message", "Type: $messageType")
                }
            }
        } catch (e: Exception) {
            addMessage(MessageType.OTHER, "Parse Error", e.message ?: "Failed to parse message")
        }
    }

    private fun addMessage(type: MessageType, title: String, description: String) {
        val timestamp = dateFormat.format(Date())
        val message = FASLitMessage(type, title, description, timestamp)
        _messages.value = _messages.value + message

        // Keep only last 100 messages
        if (_messages.value.size > 100) {
            _messages.value = _messages.value.takeLast(100)
        }
    }
}
