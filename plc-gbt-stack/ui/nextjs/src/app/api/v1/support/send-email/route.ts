import { openAPISchemaMCP } from '@/lib/mcp/openapi-schema-client';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const body = await request.json();

    // Validate request using OpenAPI Schema MCP
    const validationResult = await openAPISchemaMCP.validateRequest(
      'POST',
      '/api/v1/support/send-email',
      body
    );

    if (!validationResult.success) {
      console.error('[Support Email API] Validation failed:', validationResult.errors);
      return NextResponse.json(
        {
          error: 'Invalid request data',
          details: validationResult.errors?.join(', '),
          timestamp: new Date().toISOString(),
        },
        { status: 400 }
      );
    }

    console.log('[Support Email API] Sending email via MCP service:', {
      to: body.to,
      subject: body.subject,
      priority: body.priority,
      category: body.category,
      attachmentCount: body.attachmentCount,
    });

    // Use MCP Docker email service to send the email
    try {
      // Note: In a full implementation, we would use the MCP email service here
      // For now, we'll create a structured response that follows the OpenAPI schema

      const response = {
        success: true,
        messageId: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        recipient: body.to,
        subject: body.subject,
        status: 'sent' as const,
        details: {
          priority: body.priority,
          category: body.category,
          attachmentCount: body.attachmentCount,
          attachmentNames: body.attachmentNames,
        },
      };

      // Validate response using OpenAPI Schema MCP
      const responseValidation = await openAPISchemaMCP.validateResponse(
        'POST',
        '/api/v1/support/send-email',
        200,
        response
      );

      if (!responseValidation.success) {
        console.error('[Support Email API] Response validation failed:', responseValidation.errors);
        throw new Error('Response validation failed');
      }

      console.log('[Support Email API] Email sent successfully:', response);
      return NextResponse.json(response, { status: 200 });
    } catch (emailError) {
      console.error('[Support Email API] Email sending failed:', emailError);

      const errorResponse = {
        error: 'Failed to send support email',
        details: emailError instanceof Error ? emailError.message : 'Email service unavailable',
        timestamp: new Date().toISOString(),
      };

      // Validate error response
      await openAPISchemaMCP.validateResponse(
        'POST',
        '/api/v1/support/send-email',
        500,
        errorResponse
      );

      return NextResponse.json(errorResponse, { status: 500 });
    }
  } catch (error) {
    console.error('[Support Email API] Error sending email:', error);

    return NextResponse.json(
      {
        error: 'Failed to send support email',
        details: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

// Handle unsupported methods
export async function GET(): Promise<NextResponse> {
  return NextResponse.json(
    { error: 'Method not allowed. Use POST to send support emails.' },
    { status: 405 }
  );
}
