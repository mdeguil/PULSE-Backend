package com.pulse.backend.service;

public class AuthApiUnavailableException extends RuntimeException {
	public AuthApiUnavailableException(Throwable cause) {
		super("Authentication API request failed", cause);
	}
}
