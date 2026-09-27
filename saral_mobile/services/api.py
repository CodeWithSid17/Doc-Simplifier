import os
from typing import Optional

import httpx


class SaralAPI:

    def __init__(
        self,
        base_url: Optional[str] = None,
    ):
        self.base_url = (
            base_url
            or os.environ.get(
                "SARAL_API_URL",
                "http://127.0.0.1:8000",
            )
        ).rstrip("/")

        self.token = None

    def _headers(self):

        if not self.token:
            return {}

        return {
            "Authorization": f"Token {self.token}",
        }

    async def register(
        self,
        username,
        email,
        password,
    ):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/auth/register/",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                },
            )

        data = response.json()

        if response.status_code == 201:

            self.token = data["token"]

        return response.status_code, data

    async def login(
        self,
        email,
        password,
    ):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/auth/login/",
                json={
                    "email": email,
                    "password": password,
                },
            )

        data = response.json()

        if response.status_code == 200:

            self.token = data["token"]

        return response.status_code, data

    async def logout(self):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/auth/logout/",
                headers=self._headers(),
            )

        self.token = None

        return response.status_code

    async def me(self):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.get(
                f"{self.base_url}/api/auth/me/",
                headers=self._headers(),
            )

        return response.status_code, response.json()

    async def simplify(
        self,
        text,
        audience="adult",
        language="en",
    ):

        async with httpx.AsyncClient(
            timeout=90
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/simplify/",
                json={
                    "text": text,
                    "audience": audience,
                    "language": language,
                },
            )

        return response.status_code, response.json()

    async def upload_document(
        self,
        file_path,
        file_name,
        audience="adult",
        language="en",
    ):

        with open(
            file_path,
            "rb",
        ) as file_handle:

            files = {
                "file": (
                    file_name,
                    file_handle,
                )
            }

            data = {
                "audience": audience,
                "language": language,
            }

            async with httpx.AsyncClient(
                timeout=120
            ) as client:

                response = await client.post(
                    f"{self.base_url}/api/documents/upload/",
                    headers=self._headers(),
                    data=data,
                    files=files,
                )

        return response.status_code, response.json()

    async def extract_document(
        self,
        document_id,
    ):

        async with httpx.AsyncClient(
            timeout=120
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/documents/"
                f"{document_id}/extract/",
                headers=self._headers(),
            )

        return response.status_code, response.json()

    async def get_documents(self):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.get(
                f"{self.base_url}/api/documents/",
                headers=self._headers(),
            )

        return response.status_code, response.json()

    async def delete_document(
        self,
        document_id,
    ):

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.delete(
                f"{self.base_url}/api/documents/"
                f"{document_id}/delete/",
                headers=self._headers(),
            )

        return response.status_code