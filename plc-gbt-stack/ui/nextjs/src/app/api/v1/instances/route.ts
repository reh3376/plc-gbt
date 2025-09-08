import { controlLoopDB } from '@/lib/mock-db/control-loops';
import { NextRequest, NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';

export async function GET() {
  try {
    const instances = controlLoopDB.getAll();

    return NextResponse.json({
      success: true,
      data: {
        instances,
        total: instances.length,
      },
    });
  } catch (error) {
    console.error('Error fetching control loop instances:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch control loop instances',
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('Received control loop create request:', body);

    const { name, schema, parameters } = body;

    if (!name || !schema || !parameters) {
      console.error('Missing required fields:', {
        name: !!name,
        schema: !!schema,
        parameters: !!parameters,
      });
      return NextResponse.json(
        { success: false, error: 'Missing required fields: name, schema, parameters' },
        { status: 400 }
      );
    }

    // Generate a unique ID for the new instance
    const id = uuidv4();

    // Create the instance object
    const instance = {
      id,
      name: body.name,
      type: body.type || 'PID',
      schema: body.schema,
      parameters: body.parameters || {},
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Store in mock database
    controlLoopDB.create(instance);

    // Return success response matching the expected format
    console.log('Created control loop instance:', instance);
    return NextResponse.json({
      success: true,
      data: {
        id: instance.id,
        instance: instance, // Return the full instance as expected by client.ts
      },
    });
  } catch (error) {
    console.error('Error creating control loop instance:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to create control loop instance',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
