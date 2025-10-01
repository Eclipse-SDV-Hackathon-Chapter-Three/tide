package com.example.digitalclusterapp.feature.cluster.ui.component

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Text
import androidx.compose.ui.graphics.Color
import com.example.digitalclusterapp.R

/**
 * Displays a notification message with an icon and text.
 *
 * @param iconRes Resource ID for the warning icon
 * @param message The notification message to display
 * @param modifier Modifier for the component
 */
@Composable
fun NotificationMessage(
    iconRes: Int,
    message: String,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier,
        contentAlignment = Alignment.CenterEnd
    ) {
        Row(
            modifier = Modifier
                .padding(90.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Warning Icon
            Image(
                painter = painterResource(id = iconRes),
                contentDescription = "Warning Icon",
                contentScale = ContentScale.Fit,
                modifier = Modifier.size(24.dp)
            )

            // Notification Text
            Text(
                text = message,
                style = TextStyle(
                    color = Color.White,
                    fontSize = 16.sp
                )
            )
        }
    }
}