async def test_metrics(client):
    await client.get("/ping")
    response = await client.get("/metrics")
    text = await response.text()
    assert response.status == 200
    assert 'request_count_total{method="GET",path="/ping",status="200"} 1.0' in text
    assert 'request_latency_sum{method="GET",path="/ping"}' in text
    assert 'requests_in_progress{method="GET",path="/ping"} 0.0' in text
    assert 'requests_in_progress{method="GET",path="/metrics"} 1.0' in text
