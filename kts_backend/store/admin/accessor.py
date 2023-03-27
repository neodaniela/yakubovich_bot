import typing
from hashlib import sha256

from sqlalchemy import select

from kts_backend.admin.models import Admin, AdminModel
from kts_backend.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app
        admin = await self.get_by_email(app.config.admin.email)
        if not admin:
            await self.create_admin(
                app.config.admin.email, app.config.admin.password
            )

    async def get_by_email(self, email: str) -> Admin or None:
        async with self.app.database.session() as session:
            query = select(AdminModel).where(AdminModel.email == email)
            result = await session.execute(query)
            admin = result.scalars().first()
            if admin:
                return admin.convert_to_dataclass()

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            hash_pass = sha256(password.encode()).hexdigest()
            admin = AdminModel(email=email, password=hash_pass)
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

            return admin.convert_to_dataclass()
