/**
 * Connection Test Component
 * Tests the frontend-backend API connection
 */
import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useHealthCheck } from '@/services'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export function ConnectionTest() {
  const { data, error, isLoading, refetch } = useQuery(useHealthCheck())

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'operational':
        return 'text-green-600'
      case 'unhealthy':
      case 'down':
        return 'text-red-600'
      default:
        return 'text-yellow-600'
    }
  }

  return (
    <Card className="p-6 max-w-md mx-auto">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Backend Connection Test</h3>
          <Button 
            onClick={() => refetch()} 
            disabled={isLoading}
            size="sm"
          >
            {isLoading ? 'Testing...' : 'Test Connection'}
          </Button>
        </div>

        {isLoading && (
          <div className="text-center text-gray-600">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            Connecting to backend...
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h4 className="text-red-800 font-medium">Connection Failed</h4>
            <p className="text-red-600 text-sm mt-1">
              {error instanceof Error ? error.message : 'Unknown error occurred'}
            </p>
            <p className="text-red-500 text-xs mt-2">
              Make sure the backend is running on http://localhost:8000
            </p>
          </div>
        )}

        {data && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h4 className="text-green-800 font-medium">✅ Connection Successful!</h4>
            <div className="mt-3 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Service:</span>
                <span className="font-medium">{data.service}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Status:</span>
                <span className={`font-medium ${getStatusColor(data.status)}`}>
                  {data.status}
                </span>
              </div>
              <div className="mt-3">
                <span className="text-gray-600 text-sm">Health Checks:</span>
                <div className="ml-4 mt-1 space-y-1">
                  {Object.entries(data.checks).map(([key, check]) => {
                    const checkData = check as { status: string; [key: string]: any }
                    return (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-500 capitalize">{key}:</span>
                        <span className={`font-medium ${getStatusColor(checkData.status)}`}>
                          {checkData.status}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="text-xs text-gray-500 text-center">
          This component tests the connection to the FastAPI backend.
          <br />
          Remove this component once integration is verified.
        </div>
      </div>
    </Card>
  )
}