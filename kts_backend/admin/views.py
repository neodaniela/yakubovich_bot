from aiohttp.web import HTTPForbidden
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from kts_backend.admin.schemes import AdminSchema
from kts_backend.web.app import View
from kts_backend.web.mixins import AuthRequiredMixin
from kts_backend.web.schemes import OkResponseSchema
from kts_backend.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Admin login", description="Admin login")
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        request_data = self.request["data"]
        admin = await self.store.admins.get_by_email(request_data["email"])
        if not admin or not admin.is_password_valid(request_data["password"]):
            raise HTTPForbidden(reason="invalid credentials")
        response_data = AdminSchema().dump(admin)
        session = await new_session(request=self.request)
        session["admin"] = response_data
        return json_response(data=response_data)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"], summary="Current admin", description="Get current admin"
    )
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
