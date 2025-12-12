import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.OpenAPI;

@service(#{
  title: "Todo List API",
})
@server("http://localhost:8000", "Development server")
namespace TodoApi;

// Authentication models
model UserRegister {
  name: string;
  email: string;
  password: string;
}

model UserLogin {
  email: string;
  password: string;
}

model TokenResponse {
  token: string;
}

// Todo models
model Todo {
  id: int32;
  title: string;
  description?: string;
}

model TodoCreate {
  title: string;
  description?: string;
}

model TodoUpdate {
  title?: string;
  description?: string;
}

model TodoListResponse {
  data: Todo[];
  page: int32;
  limit: int32;
  total: int32;
}

// Error models
model ErrorResponse {
  message: string;
}

// Authentication operations
@route("/register")
interface Register {
  @post
  register(@body user: UserRegister): TokenResponse | ErrorResponse;
}

@route("/login")
interface Login {
  @post
  login(@body credentials: UserLogin): TokenResponse | ErrorResponse;
}

// Todo operations
@route("/todos")
interface Todos {
  @get
  list(
    @query page?: int32,
    @query limit?: int32
  ): TodoListResponse | ErrorResponse;

  @post
  create(@body todo: TodoCreate): Todo | ErrorResponse;
}

@route("/todos/{id}")
interface TodoById {
  @put
  update(@path id: int32, @body todo: TodoUpdate): Todo | ErrorResponse;

  @delete
  delete(@path id: int32): void | ErrorResponse;
}

