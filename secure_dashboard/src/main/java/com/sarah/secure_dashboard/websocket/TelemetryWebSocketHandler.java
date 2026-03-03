package com.sarah.secure_dashboard.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sarah.secure_dashboard.model.TelemetryData;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Simple WebSocket handler that keeps track of connected sessions per-satelliteId
 * and allows broadcasting telemetry data to every client registered for a particular
 * satellite.
 */
@Component
@Slf4j
public class TelemetryWebSocketHandler extends TextWebSocketHandler {

    private final Map<String, List<WebSocketSession>> sessions = new ConcurrentHashMap<>();
    private final ObjectMapper mapper = new ObjectMapper();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        String path = session.getUri().getPath();
        String satelliteId = extractSatelliteId(path);
        if (satelliteId != null) {
            sessions.computeIfAbsent(satelliteId, k -> new CopyOnWriteArrayList<>()).add(session);
            log.info("WebSocket connected for satellite {} (session={})", satelliteId, session.getId());
        } else {
            log.warn("Could not determine satelliteId from URI [{}]", path);
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        // remove from any lists that contain this session
        sessions.values().forEach(list -> list.remove(session));
        log.info("WebSocket closed (session={}) status={}", session.getId(), status);
    }

    public void broadcast(TelemetryData data) throws IOException {
        if (data == null || data.getSatelliteId() == null) {
            return;
        }
        List<WebSocketSession> list = sessions.get(data.getSatelliteId());
        if (list == null || list.isEmpty()) {
            return;
        }
        String payload = mapper.writeValueAsString(data);
        TextMessage message = new TextMessage(payload);
        for (WebSocketSession s : list) {
            if (s.isOpen()) {
                s.sendMessage(message);
            }
        }
    }

    private String extractSatelliteId(String path) {
        if (path == null) {
            return null;
        }
        // expected pattern: /ws/telemetry/{satelliteId}
        String[] parts = path.split("/");
        if (parts.length >= 4) {
            return parts[parts.length - 1];
        }
        return null;
    }
}
