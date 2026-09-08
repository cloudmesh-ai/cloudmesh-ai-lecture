# 8. Exercises & Assignments

!!! info "Instructions"
    Complete these exercises to apply the concepts learned in this tutorial. Submit your solutions as a GitHub repository containing your code, tests, and documentation.

---

!!! note "Assignment 1: Design Exercise"
    **Task**: Create a resource model for a simple e‑commerce system (Products, Orders, Customers). 
    - Sketch the URI hierarchy.
    - List the HTTP methods you would expose for each resource.
    - Define the expected status codes for each operation.

---

!!! note "Assignment 2: Hands‑On Coding"
    **Task**: Implement a REST service using Flask.
    - Build a book inventory service.
    - Extend the service to support **pagination** (e.g., `GET /api/books?page=2&size=5`).
    - Add **basic JWT authentication** using `PyJWT`. Protect the `POST`, `PATCH`, and `DELETE` endpoints.

---

!!! note "Assignment 3: Testing Challenge"
    **Task**: Ensure your API is robust.
    - Write an automated test suite using `pytest` and `requests` that covers all CRUD operations.
    - Include "edge case" tests (e.g., requesting a non-existent resource should return `404`).
    - Export your tests as a Postman collection.

---

!!! note "Assignment 4: Tool Comparison Report"
    **Task**: Evaluate the tooling ecosystem.
    - Perform the same set of CRUD operations against your service using two different tools (e.g., Postman & `HTTPie`).
    - Document the pros and cons of each (speed, ergonomics, scripting).
    - Recommend which tool is better for a **front-end developer** vs. a **DevOps engineer**.

---

!!! note "Assignment 5: OpenAPI Spec Creation"
    **Task**: Document your API professionally.
    - Write a full OpenAPI 3.0 specification (YAML or JSON) for your book service.
    - Use **Swagger UI** or **ReDoc** to generate interactive documentation.
    - (Bonus) Use `openapi-generator-cli` to generate a client SDK in a language of your choice.

---

### Submission Checklist
Your GitHub repository should contain:
- [ ] `app.py` (The Flask service)
- [ ] `tests/` (Folder with pytest files)
- [ ] `openapi.yaml` (The API specification)
- [ ] `README.md` (Instructions on how to run the service and tests)
