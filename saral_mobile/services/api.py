import os
from typing import Optional

import httpx


class APIError(Exception):
    def __init__(self, status_code: int, message: str, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.payload = payload or {}


class SaralAPI:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.environ.get("SARAL_API_URL", "https://doc-simplifier.onrender.com")
        ).rstrip("/")
        self.token = None

    def _headers(self):
        if not self.token:
            return {}
        return {
            "Authorization": f"Token {self.token}",
            "Accept": "application/json",
        }

    @staticmethod
    def _json(response):
        try:
            return response.json()
        except ValueError:
            return {"error": response.text or "Invalid server response."}

    def _message(self, response, data):
        if response.status_code == 401:
            return "Your session has expired. Please sign in again."
        if response.status_code == 403:
            return "You don't have permission to perform this action."
        if response.status_code == 404:
            return "The requested item was not found."
        if response.status_code == 413:
            return "This file is too large."
        if isinstance(data, dict):
            detail = data.get("error") or data.get("detail")
            if detail:
                return str(detail)
            if data:
                first = next(iter(data.values()))
                if isinstance(first, list) and first:
                    return str(first[0])
                return str(first)
        return f"Request failed with status {response.status_code}."

    async def register(self, username, email, password):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/api/auth/register/",
                json={"username": username, "email": email, "password": password},
            )
        data = self._json(response)
        if response.status_code == 201:
            self.token = data.get("token")
        return response.status_code, data

    async def login(self, email, password):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/api/auth/login/",
                json={"email": email, "password": password},
            )
        data = self._json(response)
        if response.status_code == 200:
            self.token = data.get("token")
        return response.status_code, data

    async def logout(self):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/logout/",
                    headers=self._headers(),
                )
            return response.status_code
        finally:
            self.token = None

    async def me(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/api/auth/me/",
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def simplify(self, text, audience="adult", language="en"):
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                f"{self.base_url}/api/simplify/",
                json={"text": text, "audience": audience, "language": language},
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def upload_document(self, file_path, file_name, audience="adult", language="en"):
        with open(file_path, "rb") as file_handle:
            files = {"file": (file_name, file_handle)}
            data = {"audience": audience, "language": language}
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    f"{self.base_url}/api/documents/upload/",
                    headers=self._headers(),
                    data=data,
                    files=files,
                )
        return response.status_code, self._json(response)

    async def extract_document(self, document_id):
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                f"{self.base_url}/api/documents/{document_id}/extract/",
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def get_documents(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/api/documents/",
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def get_document(self, document_id):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/api/documents/{document_id}/content/",
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def delete_document(self, document_id):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(
                f"{self.base_url}/api/documents/{document_id}/delete/",
                headers=self._headers(),
            )
        return response.status_code, self._json(response)

    async def analyze(self, text, language="en"):
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/ai/analyze/",
                headers=self._headers(),
                json={"text": text, "language": language},
            )
        return response.status_code, self._json(response)

    async def ask_document(self, document_id, question):
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/ai/chat/",
                headers=self._headers(),
                json={"document_id": document_id, "question": question},
            )
        return response.status_code, self._json(response)

    async def translate(self, text, language):
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/ai/translate/",
                headers=self._headers(),
                json={"text": text, "language": language},
            )
        return response.status_code, self._json(response)

    async def compare_documents(self, document_a_id, document_b_id):
        async with httpx.AsyncClient(timeout=150) as client:
            response = await client.post(
                f"{self.base_url}/api/ai/compare/",
                headers=self._headers(),
                json={
                    "document_a_id": document_a_id,
                    "document_b_id": document_b_id,
                },
            )
        return response.status_code, self._json(response)
