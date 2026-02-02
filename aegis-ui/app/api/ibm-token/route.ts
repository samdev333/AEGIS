import { NextResponse } from "next/server";

const IBM_API_KEY = process.env.IBM_API_KEY || "";

export async function GET() {
  try {
    const response = await fetch("https://iam.cloud.ibm.com/identity/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
      },
      body: new URLSearchParams({
        grant_type: "urn:ibm:params:oauth:grant-type:apikey",
        apikey: IBM_API_KEY,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: `Failed to get IAM token: ${response.status}`, details: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({ access_token: data.access_token });
  } catch (error) {
    console.error("Error fetching IAM token:", error);
    return NextResponse.json(
      { error: "Failed to fetch IAM token" },
      { status: 500 }
    );
  }
}
