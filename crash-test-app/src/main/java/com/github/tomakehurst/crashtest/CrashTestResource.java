package com.github.tomakehurst.crashtest;


import com.github.tomakehurst.wiremock.client.WireMock;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.util.EntityUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.core.Response;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;

import static com.github.tomakehurst.wiremock.client.WireMock.*;

@Path("/")
public class CrashTestResource {

    private static final Logger log = LoggerFactory.getLogger(CrashTestResource.class);

    private final HttpClient httpClient;
    private final String wireMockHost;

    public CrashTestResource(HttpClient httpClient, String wireMockHost, WireMock wireMock) {
        this.httpClient = httpClient;
        this.wireMockHost = wireMockHost;

        wireMock.resetMappings();
        wireMock.register(get(urlEqualTo("/something")).willReturn(
                aResponse().withStatus(200).withBody("Success").withFixedDelay(100)));
    }

    @GET
    public String root() {
        return "Uh-oh...";
    }

    @GET
    @Path("no-connect-timeout")
    public Response httpClientWithLongConnectTimeout() {
        HttpGet get = getSomething();
        HttpResponse response;
        try {
            response = httpClient.execute(get);
            return Response.ok(EntityUtils.toString(response.getEntity())).build();
        } catch (IOException ioe) {
            log.error("Failed to GET " + get.getURI(), ioe);
            return Response.serverError().entity(renderFailureMessage(ioe)).build();
        } finally {
            get.releaseConnection();
        }
    }

    @GET
    @Path("bad-http-client-error-handling")
    public String httpClientWithBadErrorHandling() {
        HttpGet get = getSomething();
        HttpResponse response;
        try {
            response = httpClient.execute(get);
            String result = EntityUtils.toString(response.getEntity());
            get.releaseConnection();
            return result;
        } catch (IOException ioe) {

            StringWriter stringWriter = new StringWriter();
            PrintWriter pw = new PrintWriter(stringWriter);
            ioe.printStackTrace(pw);
            return "Failure:\n" + stringWriter.toString();
        }
    }

    private String renderFailureMessage(IOException ioe) {
        StringWriter stringWriter = new StringWriter();
        PrintWriter pw = new PrintWriter(stringWriter);
        ioe.printStackTrace(pw);
        return "Failure:\n" + stringWriter.toString();
    }

    private HttpGet getSomething() {
        return new HttpGet("http://" + wireMockHost + ":8080/something");
    }

}
