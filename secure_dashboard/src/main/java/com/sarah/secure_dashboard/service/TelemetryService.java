package com.sarah.secure_dashboard.service;

import com.sarah.secure_dashboard.model.TelemetryData;
import com.sarah.secure_dashboard.repository.TelemetryRepository;
import com.sarah.secure_dashboard.websocket.TelemetryWebSocketHandler;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class TelemetryService {

    private final TelemetryRepository repository;
    private final TelemetryWebSocketHandler webSocketHandler;
    
    public TelemetryService(TelemetryRepository repository,
                            TelemetryWebSocketHandler webSocketHandler                        ) {
        this.repository = repository;
        this.webSocketHandler = webSocketHandler;
    }

    public TelemetryData save(TelemetryData data) {

        data.setTimestamp(LocalDateTime.now());
        

        TelemetryData saved = repository.save(data);

        try {
            webSocketHandler.broadcast(saved);
        } catch (Exception e) {
            e.printStackTrace();
        }

        return saved;
    }

    public List<TelemetryData> getAll() {
        return repository.findAll();
    }

    
}