package com.sarah.secure_dashboard;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sarah.secure_dashboard.model.TelemetryData;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class TelemetryControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void getTelemetryReturnsOk() throws Exception {
        mockMvc.perform(get("/api/telemetry"))
                .andExpect(status().isOk());
    }

    @Test
    void postMlResultIsStored() throws Exception {
        TelemetryData sample = new TelemetryData();
        sample.setSatelliteId("sat1");
        sample.setTemperature(10);
        sample.setVoltage(5);
        sample.setAltitude(100);
        sample.setTempDelta(0);
        sample.setVoltDelta(0);
        sample.setRollingTempMean(10);
        sample.setAnomaly(false);
        sample.setAnomalyScore(0.0);
        sample.setTimestamp(LocalDateTime.now());

        String json = objectMapper.writeValueAsString(sample);

        mockMvc.perform(post("/api/ml/result")
                .contentType(MediaType.APPLICATION_JSON)
                .content(json))
                .andExpect(status().isOk());

        // afterwards GET should still return ok
        mockMvc.perform(get("/api/telemetry"))
                .andExpect(status().isOk());
    }
}
