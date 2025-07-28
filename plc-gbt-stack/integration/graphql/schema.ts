/**
 * GraphQL Schema Definition
 * Phase 32.1 - Multi-System Integration
 * 
 * Type-safe GraphQL schema for PLC-GBT data queries
 * CRITICAL: No any types allowed - strict TypeScript typing enforced
 */

import { GraphQLSchema, GraphQLObjectType, GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLList, GraphQLNonNull, GraphQLID, GraphQLEnumType, GraphQLInputObjectType } from 'graphql'
import { DateTimeResolver, JSONResolver } from 'graphql-scalars'

// Enums
const PLCStatusEnum = new GraphQLEnumType({
  name: 'PLCStatus',
  values: {
    ONLINE: { value: 'online' },
    OFFLINE: { value: 'offline' },
    FAULT: { value: 'fault' },
    MAINTENANCE: { value: 'maintenance' }
  }
})

const ControlLoopModeEnum = new GraphQLEnumType({
  name: 'ControlLoopMode',
  values: {
    AUTO: { value: 'auto' },
    MANUAL: { value: 'manual' },
    CASCADE: { value: 'cascade' }
  }
})

const DataQualityEnum = new GraphQLEnumType({
  name: 'DataQuality',
  values: {
    GOOD: { value: 'good' },
    BAD: { value: 'bad' },
    UNCERTAIN: { value: 'uncertain' }
  }
})

// Types
const PLCType = new GraphQLObjectType({
  name: 'PLC',
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: new GraphQLNonNull(GraphQLString) },
    status: { type: new GraphQLNonNull(PLCStatusEnum) },
    ipAddress: { type: new GraphQLNonNull(GraphQLString) },
    model: { type: GraphQLString },
    firmware: { type: GraphQLString },
    cpuUsage: { type: GraphQLFloat },
    memoryUsage: { type: GraphQLFloat },
    lastSeen: { type: DateTimeResolver },
    tags: {
      type: new GraphQLList(TagType),
      args: {
        limit: { type: GraphQLInt, defaultValue: 100 },
        offset: { type: GraphQLInt, defaultValue: 0 }
      },
      resolve: async (parent, args, context) => {
        return context.dataSources.plcAPI.getTagsByPLC(parent.id, args)
      }
    }
  })
})

const TagType = new GraphQLObjectType({
  name: 'Tag',
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: new GraphQLNonNull(GraphQLString) },
    plcId: { type: new GraphQLNonNull(GraphQLID) },
    dataType: { type: new GraphQLNonNull(GraphQLString) },
    value: { type: JSONResolver },
    quality: { type: new GraphQLNonNull(DataQualityEnum) },
    timestamp: { type: new GraphQLNonNull(DateTimeResolver) },
    unit: { type: GraphQLString },
    description: { type: GraphQLString },
    historicalData: {
      type: new GraphQLList(DataPointType),
      args: {
        startTime: { type: new GraphQLNonNull(DateTimeResolver) },
        endTime: { type: new GraphQLNonNull(DateTimeResolver) },
        interval: { type: GraphQLInt, defaultValue: 60 }
      },
      resolve: async (parent, args, context) => {
        return context.dataSources.timeSeriesDB.getHistoricalData(parent.id, args)
      }
    }
  })
})

const DataPointType = new GraphQLObjectType({
  name: 'DataPoint',
  fields: () => ({
    timestamp: { type: new GraphQLNonNull(DateTimeResolver) },
    value: { type: new GraphQLNonNull(JSONResolver) },
    quality: { type: new GraphQLNonNull(DataQualityEnum) }
  })
})

const ControlLoopType = new GraphQLObjectType({
  name: 'ControlLoop',
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    name: { type: new GraphQLNonNull(GraphQLString) },
    plcId: { type: new GraphQLNonNull(GraphQLID) },
    mode: { type: new GraphQLNonNull(ControlLoopModeEnum) },
    setpoint: { type: new GraphQLNonNull(GraphQLFloat) },
    processVariable: { type: new GraphQLNonNull(GraphQLFloat) },
    controlVariable: { type: new GraphQLNonNull(GraphQLFloat) },
    pidParameters: { type: PIDParametersType },
    status: { type: new GraphQLNonNull(GraphQLString) },
    performance: { type: PerformanceMetricsType },
    lastTuned: { type: DateTimeResolver }
  })
})

const PIDParametersType = new GraphQLObjectType({
  name: 'PIDParameters',
  fields: () => ({
    kp: { type: new GraphQLNonNull(GraphQLFloat) },
    ki: { type: new GraphQLNonNull(GraphQLFloat) },
    kd: { type: new GraphQLNonNull(GraphQLFloat) },
    deadband: { type: GraphQLFloat },
    outputMin: { type: GraphQLFloat },
    outputMax: { type: GraphQLFloat }
  })
})

const PerformanceMetricsType = new GraphQLObjectType({
  name: 'PerformanceMetrics',
  fields: () => ({
    overshoot: { type: GraphQLFloat },
    settlingTime: { type: GraphQLFloat },
    steadyStateError: { type: GraphQLFloat },
    oscillationIndex: { type: GraphQLFloat }
  })
})

const AlarmType = new GraphQLObjectType({
  name: 'Alarm',
  fields: () => ({
    id: { type: new GraphQLNonNull(GraphQLID) },
    tagId: { type: new GraphQLNonNull(GraphQLID) },
    severity: { type: new GraphQLNonNull(GraphQLString) },
    message: { type: new GraphQLNonNull(GraphQLString) },
    timestamp: { type: new GraphQLNonNull(DateTimeResolver) },
    acknowledged: { type: new GraphQLNonNull(GraphQLBoolean) },
    acknowledgedBy: { type: GraphQLString },
    acknowledgedAt: { type: DateTimeResolver }
  })
})

// Input Types
const TagFilterInput = new GraphQLInputObjectType({
  name: 'TagFilterInput',
  fields: () => ({
    plcId: { type: GraphQLID },
    nameContains: { type: GraphQLString },
    dataType: { type: GraphQLString },
    quality: { type: DataQualityEnum }
  })
})

const ControlLoopUpdateInput = new GraphQLInputObjectType({
  name: 'ControlLoopUpdateInput',
  fields: () => ({
    mode: { type: ControlLoopModeEnum },
    setpoint: { type: GraphQLFloat },
    pidParameters: { type: PIDParametersUpdateInput }
  })
})

const PIDParametersUpdateInput = new GraphQLInputObjectType({
  name: 'PIDParametersUpdateInput',
  fields: () => ({
    kp: { type: GraphQLFloat },
    ki: { type: GraphQLFloat },
    kd: { type: GraphQLFloat }
  })
})

// Queries
const QueryType = new GraphQLObjectType({
  name: 'Query',
  fields: () => ({
    // PLC Queries
    plc: {
      type: PLCType,
      args: { id: { type: new GraphQLNonNull(GraphQLID) } },
      resolve: async (_, args, context) => {
        return context.dataSources.plcAPI.getPLC(args.id)
      }
    },
    plcs: {
      type: new GraphQLList(PLCType),
      args: {
        status: { type: PLCStatusEnum },
        limit: { type: GraphQLInt, defaultValue: 50 },
        offset: { type: GraphQLInt, defaultValue: 0 }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.plcAPI.getPLCs(args)
      }
    },
    
    // Tag Queries
    tag: {
      type: TagType,
      args: { id: { type: new GraphQLNonNull(GraphQLID) } },
      resolve: async (_, args, context) => {
        return context.dataSources.plcAPI.getTag(args.id)
      }
    },
    tags: {
      type: new GraphQLList(TagType),
      args: {
        filter: { type: TagFilterInput },
        limit: { type: GraphQLInt, defaultValue: 100 },
        offset: { type: GraphQLInt, defaultValue: 0 }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.plcAPI.getTags(args)
      }
    },
    
    // Control Loop Queries
    controlLoop: {
      type: ControlLoopType,
      args: { id: { type: new GraphQLNonNull(GraphQLID) } },
      resolve: async (_, args, context) => {
        return context.dataSources.controlAPI.getControlLoop(args.id)
      }
    },
    controlLoops: {
      type: new GraphQLList(ControlLoopType),
      args: {
        plcId: { type: GraphQLID },
        mode: { type: ControlLoopModeEnum },
        limit: { type: GraphQLInt, defaultValue: 50 },
        offset: { type: GraphQLInt, defaultValue: 0 }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.controlAPI.getControlLoops(args)
      }
    },
    
    // Alarm Queries
    activeAlarms: {
      type: new GraphQLList(AlarmType),
      args: {
        severity: { type: GraphQLString },
        unacknowledgedOnly: { type: GraphQLBoolean, defaultValue: false }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.alarmAPI.getActiveAlarms(args)
      }
    },
    
    // System Status
    systemStatus: {
      type: new GraphQLObjectType({
        name: 'SystemStatus',
        fields: () => ({
          plcCount: { type: GraphQLInt },
          activeTags: { type: GraphQLInt },
          activeAlarms: { type: GraphQLInt },
          dataRate: { type: GraphQLFloat },
          uptime: { type: GraphQLInt }
        })
      }),
      resolve: async (_, __, context) => {
        return context.dataSources.systemAPI.getSystemStatus()
      }
    }
  })
})

// Mutations
const MutationType = new GraphQLObjectType({
  name: 'Mutation',
  fields: () => ({
    // Control Loop Mutations
    updateControlLoop: {
      type: ControlLoopType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLID) },
        input: { type: new GraphQLNonNull(ControlLoopUpdateInput) }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.controlAPI.updateControlLoop(args.id, args.input)
      }
    },
    tuneControlLoop: {
      type: ControlLoopType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLID) },
        method: { type: GraphQLString, defaultValue: 'auto' }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.controlAPI.tuneControlLoop(args.id, args.method)
      }
    },
    
    // Tag Mutations
    writeTag: {
      type: TagType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLID) },
        value: { type: new GraphQLNonNull(JSONResolver) }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.plcAPI.writeTag(args.id, args.value)
      }
    },
    
    // Alarm Mutations
    acknowledgeAlarm: {
      type: AlarmType,
      args: {
        id: { type: new GraphQLNonNull(GraphQLID) },
        acknowledgedBy: { type: new GraphQLNonNull(GraphQLString) }
      },
      resolve: async (_, args, context) => {
        return context.dataSources.alarmAPI.acknowledgeAlarm(args.id, args.acknowledgedBy)
      }
    }
  })
})

// Subscriptions
const SubscriptionType = new GraphQLObjectType({
  name: 'Subscription',
  fields: () => ({
    tagValueChanged: {
      type: TagType,
      args: { tagId: { type: new GraphQLNonNull(GraphQLID) } },
      subscribe: async (_, args, context) => {
        return context.pubsub.asyncIterator([`TAG_VALUE_CHANGED_${args.tagId}`])
      }
    },
    controlLoopUpdated: {
      type: ControlLoopType,
      args: { loopId: { type: new GraphQLNonNull(GraphQLID) } },
      subscribe: async (_, args, context) => {
        return context.pubsub.asyncIterator([`CONTROL_LOOP_UPDATED_${args.loopId}`])
      }
    },
    newAlarm: {
      type: AlarmType,
      subscribe: async (_, __, context) => {
        return context.pubsub.asyncIterator(['NEW_ALARM'])
      }
    }
  })
})

// Create and export schema
export const schema = new GraphQLSchema({
  query: QueryType,
  mutation: MutationType,
  subscription: SubscriptionType
})

// Type exports for resolvers
export interface GraphQLContext {
  dataSources: {
    plcAPI: PLCDataSource
    controlAPI: ControlLoopDataSource
    alarmAPI: AlarmDataSource
    systemAPI: SystemDataSource
    timeSeriesDB: TimeSeriesDataSource
  }
  pubsub: PubSubEngine
}

interface PLCDataSource {
  getPLC(id: string): Promise<PLC>
  getPLCs(args: { status?: string; limit: number; offset: number }): Promise<PLC[]>
  getTag(id: string): Promise<Tag>
  getTags(args: { filter?: TagFilter; limit: number; offset: number }): Promise<Tag[]>
  getTagsByPLC(plcId: string, args: { limit: number; offset: number }): Promise<Tag[]>
  writeTag(id: string, value: unknown): Promise<Tag>
}

interface ControlLoopDataSource {
  getControlLoop(id: string): Promise<ControlLoop>
  getControlLoops(args: { plcId?: string; mode?: string; limit: number; offset: number }): Promise<ControlLoop[]>
  updateControlLoop(id: string, input: ControlLoopUpdate): Promise<ControlLoop>
  tuneControlLoop(id: string, method: string): Promise<ControlLoop>
}

interface AlarmDataSource {
  getActiveAlarms(args: { severity?: string; unacknowledgedOnly: boolean }): Promise<Alarm[]>
  acknowledgeAlarm(id: string, acknowledgedBy: string): Promise<Alarm>
}

interface SystemDataSource {
  getSystemStatus(): Promise<SystemStatus>
}

interface TimeSeriesDataSource {
  getHistoricalData(tagId: string, args: { startTime: Date; endTime: Date; interval: number }): Promise<DataPoint[]>
}

interface PubSubEngine {
  asyncIterator<T>(topics: string | string[]): AsyncIterator<T>
  publish(topic: string, payload: unknown): Promise<void>
}

// Type definitions
interface PLC {
  id: string
  name: string
  status: string
  ipAddress: string
  model?: string
  firmware?: string
  cpuUsage?: number
  memoryUsage?: number
  lastSeen?: Date
}

interface Tag {
  id: string
  name: string
  plcId: string
  dataType: string
  value: unknown
  quality: string
  timestamp: Date
  unit?: string
  description?: string
}

interface ControlLoop {
  id: string
  name: string
  plcId: string
  mode: string
  setpoint: number
  processVariable: number
  controlVariable: number
  pidParameters?: PIDParameters
  status: string
  performance?: PerformanceMetrics
  lastTuned?: Date
}

interface PIDParameters {
  kp: number
  ki: number
  kd: number
  deadband?: number
  outputMin?: number
  outputMax?: number
}

interface PerformanceMetrics {
  overshoot?: number
  settlingTime?: number
  steadyStateError?: number
  oscillationIndex?: number
}

interface Alarm {
  id: string
  tagId: string
  severity: string
  message: string
  timestamp: Date
  acknowledged: boolean
  acknowledgedBy?: string
  acknowledgedAt?: Date
}

interface DataPoint {
  timestamp: Date
  value: unknown
  quality: string
}

interface SystemStatus {
  plcCount: number
  activeTags: number
  activeAlarms: number
  dataRate: number
  uptime: number
}

interface TagFilter {
  plcId?: string
  nameContains?: string
  dataType?: string
  quality?: string
}

interface ControlLoopUpdate {
  mode?: string
  setpoint?: number
  pidParameters?: Partial<PIDParameters>
} 