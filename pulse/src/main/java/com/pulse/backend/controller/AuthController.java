package com.pulse.backend.controller;

import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.pulse.backend.dto.LoginRequest;
import com.pulse.backend.service.AuthApiClient;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {
	private final AuthApiClient authApiClient;

	public AuthController(AuthApiClient authApiClient) {
		this.authApiClient = authApiClient;
	}

	@PostMapping("/login")
	public ResponseEntity<byte[]> login(@Valid @RequestBody LoginRequest request) {
		return authApiClient.login(request);
	}

	@GetMapping("/me")
	public ResponseEntity<byte[]> currentUser(
			@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false)
			String authorization) {
		return authApiClient.currentUser(authorization);
	}
}
