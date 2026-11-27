package com.pulse.backend.service;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import com.pulse.backend.dto.LoginRequest;

@Service
public class AuthApiClient {
	private final RestClient restClient;

	public AuthApiClient(
			RestClient.Builder builder,
			@Value("${pulse.auth-api.base-url}") String baseUrl) {
		this.restClient = builder.baseUrl(baseUrl).build();
	}

	public ResponseEntity<byte[]> login(LoginRequest loginRequest) {
		try {
			return restClient.post()
					.uri("/api/v1/auth/login")
					.contentType(MediaType.APPLICATION_JSON)
					.body(loginRequest)
					.exchange((request, response) -> forward(response));
		} catch (RestClientException exception) {
			throw new AuthApiUnavailableException(exception);
		}
	}

	public ResponseEntity<byte[]> currentUser(String authorization) {
		try {
			return restClient.get()
					.uri("/api/v1/auth/me")
					.headers(headers -> {
						if (authorization != null) {
							headers.set(HttpHeaders.AUTHORIZATION, authorization);
						}
					})
					.exchange((request, response) -> forward(response));
		} catch (RestClientException exception) {
			throw new AuthApiUnavailableException(exception);
		}
	}

	private ResponseEntity<byte[]> forward(
			org.springframework.http.client.ClientHttpResponse response) throws IOException {
		MediaType contentType = response.getHeaders().getContentType();
		return ResponseEntity.status(response.getStatusCode())
				.contentType(contentType != null ? contentType : MediaType.APPLICATION_JSON)
				.body(response.getBody().readAllBytes());
	}
}
