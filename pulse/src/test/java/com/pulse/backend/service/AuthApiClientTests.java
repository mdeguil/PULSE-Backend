package com.pulse.backend.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.http.HttpMethod.GET;
import static org.springframework.http.HttpMethod.POST;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import java.nio.charset.StandardCharsets;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.HttpStatus;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import com.pulse.backend.dto.LoginRequest;

class AuthApiClientTests {
	private MockRestServiceServer server;
	private AuthApiClient client;

	@BeforeEach
	void setUp() {
		RestClient.Builder builder = RestClient.builder();
		server = MockRestServiceServer.bindTo(builder).build();
		client = new AuthApiClient(builder, "https://auth.example.test");
	}

	@Test
	void forwardsLoginPayloadAndReturnsApiTokenResponse() {
		String responseBody = """
				{"userId":"usr-10027","email":"user@example.test","displayName":"Test User",
				"role":"USER","accountStatus":"ACTIVE","accessToken":"demo-token-usr-10027",
				"tokenType":"Bearer","expiresIn":3600}
				""";
		server.expect(requestTo("https://auth.example.test/api/v1/auth/login"))
				.andExpect(method(POST))
				.andExpect(content().json(
						"{\"email\":\"user@example.test\",\"password\":\"secret\"}"))
				.andRespond(withSuccess(responseBody, MediaType.APPLICATION_JSON));

		var response = client.login(new LoginRequest("user@example.test", "secret"));

		assertThat(response.getStatusCode().value()).isEqualTo(200);
		assertThat(MediaType.APPLICATION_JSON.isCompatibleWith(
				response.getHeaders().getContentType())).isTrue();
		assertThat(new String(response.getBody(), StandardCharsets.UTF_8))
				.contains("\"accessToken\":\"demo-token-usr-10027\"");
		server.verify();
	}

	@Test
	void forwardsAuthenticationErrorsWithoutChangingTheirStatusOrBody() {
		String errorBody = """
				{"code":"AUTH_INVALID_CREDENTIALS","message":"Invalid credentials"}
				""";
		server.expect(requestTo("https://auth.example.test/api/v1/auth/login"))
				.andRespond(withStatus(HttpStatus.UNAUTHORIZED)
						.contentType(MediaType.APPLICATION_JSON)
						.body(errorBody));

		var response = client.login(new LoginRequest("user@example.test", "wrong"));

		assertThat(response.getStatusCode().value()).isEqualTo(401);
		assertThat(new String(response.getBody(), StandardCharsets.UTF_8))
				.contains("AUTH_INVALID_CREDENTIALS");
		server.verify();
	}

	@Test
	void forwardsBearerTokenWhenLookingUpCurrentUser() {
		server.expect(requestTo("https://auth.example.test/api/v1/auth/me"))
				.andExpect(method(GET))
				.andExpect(header(HttpHeaders.AUTHORIZATION, "Bearer demo-token-usr-10027"))
				.andRespond(withSuccess(
						"{\"userId\":\"usr-10027\"}", MediaType.APPLICATION_JSON));

		var response = client.currentUser("Bearer demo-token-usr-10027");

		assertThat(response.getStatusCode().value()).isEqualTo(200);
		assertThat(new String(response.getBody(), StandardCharsets.UTF_8))
				.contains("usr-10027");
		server.verify();
	}
}
