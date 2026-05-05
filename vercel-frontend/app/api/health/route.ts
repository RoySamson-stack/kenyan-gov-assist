import { NextResponse } from "next/server";

export async function GET() {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
    const response = await fetch(`${baseUrl}/api/health`);
    
    if (!response.ok) {
      return NextResponse.json(
        { status: "unhealthy" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { status: "unreachable", error: String(error) },
      { status: 503 }
    );
  }
}
