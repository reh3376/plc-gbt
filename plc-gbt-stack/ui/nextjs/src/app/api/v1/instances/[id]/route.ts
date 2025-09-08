import { controlLoopDB } from '@/lib/mock-db/control-loops';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const instance = controlLoopDB.get(id);

    if (!instance) {
      return NextResponse.json(
        { success: false, error: 'Control loop instance not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: instance,
    });
  } catch (error) {
    console.error('Error fetching control loop instance:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch control loop instance' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = await request.json();
    const instance = controlLoopDB.get(id);

    if (!instance) {
      return NextResponse.json(
        { success: false, error: 'Control loop instance not found' },
        { status: 404 }
      );
    }

    // Update the instance
    const updatedInstance = controlLoopDB.update(id, body);

    return NextResponse.json({
      success: true,
      data: updatedInstance,
    });
  } catch (error) {
    console.error('Error updating control loop instance:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update control loop instance' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const deleted = controlLoopDB.delete(id);

    if (!deleted) {
      return NextResponse.json(
        { success: false, error: 'Control loop instance not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Control loop instance deleted successfully',
    });
  } catch (error) {
    console.error('Error deleting control loop instance:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to delete control loop instance' },
      { status: 500 }
    );
  }
}
