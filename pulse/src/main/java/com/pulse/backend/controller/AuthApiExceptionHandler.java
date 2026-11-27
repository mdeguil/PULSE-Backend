package com.pulse.backend.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.pulse.backend.dto.AuthApiError;
import com.pulse.backend.service.AuthApiUnavailableException;

@RestControllerAdvice
public class AuthApiExceptionHandler {
	private static final Logger logger = LoggerFactory.getLogger(AuthApiExceptionHandler.class);

	@ExceptionHandler(AuthApiUnavailableException.class)
	public ResponseEntity<AuthApiError> authenticationApiUnavailable(
			AuthApiUnavailableException exception) {
		logger.warn("Authentication API is unavailable", exception);
		return ResponseEntity.status(503).body(new AuthApiError(
				"AUTH_SERVICE_UNAVAILABLE",
				"Authentication service temporarily unavailable"));
	}

	@ExceptionHandler({
			HttpMessageNotReadableException.class,
			MethodArgumentNotValidException.class
	})
	public ResponseEntity<AuthApiError> invalidAuthenticationRequest(Exception exception) {
		return ResponseEntity.badRequest().body(new AuthApiError(
				"AUTH_BAD_REQUEST",
				"Invalid authentication request"));
	}
}
