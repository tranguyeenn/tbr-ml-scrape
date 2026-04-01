import { NextResponse } from "next/server";

import { backendBaseUrl } from "../../../lib/backendUrl";
import { upstreamUnreachableResponse } from "../../../lib/upstreamError";

export async function GET() {
  try {
    const upstream = await fetch(`${backendBaseUrl()}/recommend`, {
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
