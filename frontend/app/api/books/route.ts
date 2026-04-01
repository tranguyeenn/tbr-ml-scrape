import { NextRequest, NextResponse } from "next/server";

import { backendBaseUrl } from "../../../lib/backendUrl";
import { upstreamUnreachableResponse } from "../../../lib/upstreamError";

export async function GET() {
  try {
    const upstream = await fetch(`${backendBaseUrl()}/books`, {
      method: "GET",
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return upstreamUnreachableResponse();
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const upstream = await fetch(`${backendBaseUrl()}/books`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body),
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return upstreamUnreachableResponse();
  }
}

export async function PATCH(req: NextRequest) {
  try {
    const body = await req.json();
    const upstream = await fetch(`${backendBaseUrl()}/books`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body),
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return upstreamUnreachableResponse();
  }
}

export async function DELETE(req: NextRequest) {
  const title = req.nextUrl.searchParams.get("title");
  if (!title?.trim()) {
    return NextResponse.json({ detail: "Query parameter 'title' is required." }, { status: 400 });
  }

  try {
    const url = new URL("/books", backendBaseUrl());
    url.searchParams.set("title", title);

    const upstream = await fetch(url.toString(), {
      method: "DELETE",
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return upstreamUnreachableResponse();
  }
}
