package com.routesandbox.backend;

import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@RestController
@RequestMapping("/routes")
public class RouteController {

    private final WebClient webClient = WebClient.create("http://localhost:8000");

    @PostMapping("/optimize")
    public Mono<ResponseEntity<String>> optimizeRoute(@RequestBody Map<String, Object> requestData) {
        return webClient.post().uri("/optimize")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(requestData)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .map(error -> new RuntimeException("Client error from optimizer: " + error))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .map(error -> new RuntimeException("Server error from optimizer: " + error))
                )
                .bodyToMono(String.class)
                .map(ResponseEntity::ok)
                .onErrorResume(ex -> {
                    String fallbackMessage = "Could not connect to optimizer service.";
                    String detailed = ex.getMessage();

                    String message = detailed != null
                            ? fallbackMessage + " Details: " + detailed
                            : fallbackMessage;

                    return Mono.just(ResponseEntity
                            .status(HttpStatus.SERVICE_UNAVAILABLE)
                            .body(message));
                });
    }

}
