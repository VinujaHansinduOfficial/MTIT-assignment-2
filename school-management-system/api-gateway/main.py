from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="School Management API Gateway")

SERVICE_MAP = {
    "students": "http://127.0.0.1:8001",
    "teachers": "http://127.0.0.1:8002",
    "courses": "http://127.0.0.1:8003",
    "subjects": "http://127.0.0.1:8003",
    "enrollments": "http://127.0.0.1:8004",
}

@app.get("/")
def root():
    return {
        "message": "API Gateway is running",
        "routes": {
            "/students": "Student Service",
            "/teachers": "Teacher Service",
            "/courses": "Course Service",
            "/subjects": "Course Service",
            "/enrollments": "Enrollment Service",
        },
    }

async def proxy_request(request: Request, service_url: str, path: str = ""):
    target_url = f"{service_url}{request.url.path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                timeout=30.0,
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type"),
            )
        except httpx.RequestError:
            return Response(
                content=b'{"error":"Service unavailable"}',
                status_code=503,
                media_type="application/json",
            )

@app.api_route("/students", methods=["GET", "POST"])
@app.api_route("/students/{path:path}", methods=["GET", "PUT", "DELETE", "PATCH"])
async def student_proxy(request: Request, path: str = ""):
    return await proxy_request(request, SERVICE_MAP["students"], path)

@app.api_route("/teachers", methods=["GET", "POST"])
@app.api_route("/teachers/{path:path}", methods=["GET", "PUT", "DELETE", "PATCH"])
async def teacher_proxy(request: Request, path: str = ""):
    return await proxy_request(request, SERVICE_MAP["teachers"], path)

@app.api_route("/courses", methods=["GET", "POST"])
@app.api_route("/courses/{path:path}", methods=["GET", "PUT", "DELETE", "PATCH"])
async def course_proxy(request: Request, path: str = ""):
    return await proxy_request(request, SERVICE_MAP["courses"], path)

@app.api_route("/subjects", methods=["GET", "POST"])
@app.api_route("/subjects/{path:path}", methods=["GET", "PUT", "DELETE", "PATCH"])
async def subject_proxy(request: Request, path: str = ""):
    return await proxy_request(request, SERVICE_MAP["subjects"], path)

@app.api_route("/enrollments", methods=["GET", "POST"])
@app.api_route("/enrollments/{path:path}", methods=["GET", "PUT", "DELETE", "PATCH"])
async def enrollment_proxy(request: Request, path: str = ""):
    return await proxy_request(request, SERVICE_MAP["enrollments"], path)