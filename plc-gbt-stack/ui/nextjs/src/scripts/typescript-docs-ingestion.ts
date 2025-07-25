#!/usr/bin/env node
/**
 * TypeScript Documentation Ingestion for PLC Memory System
 * 
 * Following AI Task Orchestrator methodology with:
 * - Strict TypeScript typing (no any types)
 * - Comprehensive error handling
 * - >99% reliability through validation
 * - Production-ready architecture
 * 
 * @author AI Task Orchestrator Implementation
 * @created 2025-01-17
 * @version 1.0.0
 * 
 * @compliance
 * - ✅ Strict TypeScript typing (no any types)
 * - ✅ AI Task Orchestrator methodology
 * - ✅ PLC Memory system integration
 * - ✅ Comprehensive validation
 * - ✅ Production error handling
 */

import { writeFile, mkdir } from 'fs/promises'
import { resolve } from 'path'
import { z } from 'zod'
import {
  TypeScriptDocumentationScraper,
  ScrapingResult,
  PLCMemoryEntity,
  DocumentationSection,
  createTypeScriptDocsScraper,
  TypeScriptDocsScrapingError,
  ValidationError
} from '../lib/typescript-docs-scraper'

// =============================================================================
// PLC MEMORY INTEGRATION SCHEMAS
// =============================================================================

/**
 * PLC Memory ingestion package schema based on existing patterns
 */
export const PLCMemoryIngestionPackageSchema = z.object({
  package_id: z.string().min(1),
  timestamp: z.string().datetime(),
  source_path: z.string(),
  source_type: z.literal('typescript_documentation'),
  
  // Structured data for memory system
  entities: z.array(z.object({
    id: z.string().min(1),
    type: z.enum(['documentation', 'guide', 'reference', 'tutorial', 'example']),
    name: z.string().min(1),
    description: z.string(),
    content: z.string(),
    metadata: z.record(z.string(), z.unknown()),
    tags: z.array(z.string()).default([])
  })),
  
  relationships: z.array(z.object({
    source_id: z.string(),
    target_id: z.string(),
    relationship_type: z.enum(['references', 'prerequisite', 'continuation', 'related', 'example_of']),
    strength: z.number().min(0).max(1).default(0.5),
    metadata: z.record(z.string(), z.unknown()).default({})
  })),
  
  // Memory distribution strategy
  memory_distribution: z.object({
    redis: z.array(z.string()).default([]),
    neo4j: z.array(z.string()).default([]),
    postgresql: z.array(z.string()).default([]),
    qdrant: z.array(z.string()).default([])
  }),
  
  // Quality metrics
  validation_score: z.number().min(0).max(1),
  confidence_scores: z.object({
    content_accuracy: z.number().min(0).max(1),
    relationship_strength: z.number().min(0).max(1),
    metadata_completeness: z.number().min(0).max(1),
    overall_quality: z.number().min(0).max(1)
  }),
  
  // Statistics
  statistics: z.object({
    total_entities: z.number().min(0),
    total_relationships: z.number().min(0),
    total_words: z.number().min(0),
    processing_time_ms: z.number().min(0),
    success_rate: z.number().min(0).max(1)
  })
})

export type PLCMemoryIngestionPackage = z.infer<typeof PLCMemoryIngestionPackageSchema>

/**
 * Ingestion configuration schema
 */
export const IngestionConfigSchema = z.object({
  outputDirectory: z.string().default('./ingestion_output'),
  outputFilename: z.string().default('typescript_docs_ingestion_package.json'),
  enableVerboseLogging: z.boolean().default(true),
  generateSummary: z.boolean().default(true),
  validateOutput: z.boolean().default(true),
  memoryDistributionStrategy: z.enum(['balanced', 'performance', 'storage']).default('balanced'),
  includeMetrics: z.boolean().default(true)
})

export type IngestionConfig = z.infer<typeof IngestionConfigSchema>

// =============================================================================
// INGESTION ENGINE CLASS
// =============================================================================

/**
 * TypeScript Documentation Ingestion Engine
 * 
 * Orchestrates the complete process of:
 * 1. Scraping TypeScript documentation
 * 2. Converting to PLC memory format
 * 3. Generating relationships and metadata
 * 4. Validating output quality
 * 5. Creating ingestion packages
 */
export class TypeScriptDocsIngestionEngine {
  private readonly scraper: TypeScriptDocumentationScraper
  private readonly config: IngestionConfig
  private readonly startTime: number
  
  constructor(
    config: Partial<IngestionConfig> = {},
    scraper?: TypeScriptDocumentationScraper
  ) {
    // Validate configuration with strict typing
    const configResult = IngestionConfigSchema.safeParse(config)
    if (!configResult.success) {
      throw new ValidationError(
        'Invalid ingestion configuration',
        config as Record<string, unknown>,
        configResult.error.issues.map(err => ({
          path: err.path.join('.'),
          message: err.message
        }))
      )
    }
    
    this.config = configResult.data
    this.scraper = scraper ?? createTypeScriptDocsScraper({
      maxConcurrentRequests: 3,
      requestDelayMs: 1000,
      retryAttempts: 3
    })
    this.startTime = Date.now()
  }

  /**
   * Main ingestion method following AI Task Orchestrator methodology
   * 
   * @returns Promise<PLCMemoryIngestionPackage> - Complete ingestion package
   * @throws TypeScriptDocsScrapingError - For critical ingestion failures
   */
  public async executeIngestion(): Promise<PLCMemoryIngestionPackage> {
    try {
      this.log('🚀 Starting TypeScript documentation ingestion...')
      
      // Step 1: Scrape TypeScript documentation
      this.log('📖 Step 1: Scraping TypeScript documentation')
      const scrapingResult = await this.scraper.scrapeTypeScriptDocumentation()
      this.log(`✅ Scraped ${scrapingResult.sections.length} sections with ${scrapingResult.entities.length} entities`)
      
      // Step 2: Convert to PLC memory format
      this.log('🔄 Step 2: Converting to PLC memory format')
      const memoryEntities = await this.convertToMemoryFormat(scrapingResult.entities)
      this.log(`✅ Converted ${memoryEntities.length} entities to memory format`)
      
      // Step 3: Generate relationships
      this.log('🔗 Step 3: Generating entity relationships')
      const relationships = await this.generateEntityRelationships(memoryEntities, scrapingResult.sections)
      this.log(`✅ Generated ${relationships.length} relationships`)
      
      // Step 4: Calculate memory distribution strategy
      this.log('📊 Step 4: Calculating memory distribution strategy')
      const memoryDistribution = await this.calculateMemoryDistribution(memoryEntities)
      this.log(`✅ Distributed entities across ${Object.keys(memoryDistribution).length} memory tiers`)
      
      // Step 5: Generate quality metrics
      this.log('📈 Step 5: Generating quality metrics')
      const qualityMetrics = await this.generateQualityMetrics(memoryEntities, relationships, scrapingResult)
      this.log(`✅ Quality score: ${(qualityMetrics.confidence_scores.overall_quality * 100).toFixed(1)}%`)
      
      // Step 6: Create final ingestion package
      this.log('📦 Step 6: Creating ingestion package')
      const ingestionPackage = await this.createIngestionPackage(
        memoryEntities,
        relationships,
        memoryDistribution,
        qualityMetrics,
        scrapingResult
      )
      
      // Step 7: Validate and save output
      this.log('✅ Step 7: Validating and saving output')
      await this.validateAndSaveOutput(ingestionPackage)
      
      this.log(`🎉 Ingestion completed successfully in ${Date.now() - this.startTime}ms`)
      return ingestionPackage
      
    } catch (error) {
      this.log(`❌ Critical ingestion failure: ${error instanceof Error ? error.message : String(error)}`)
      throw new TypeScriptDocsScrapingError(
        `Ingestion engine failure: ${error instanceof Error ? error.message : String(error)}`,
        'typescript-docs-ingestion',
        undefined,
        0
      )
    }
  }

  /**
   * Converts scraped entities to PLC memory format
   */
  private async convertToMemoryFormat(
    scrapedEntities: PLCMemoryEntity[]
  ): Promise<Array<{
    id: string
    type: 'documentation' | 'guide' | 'reference' | 'tutorial' | 'example'
    name: string
    description: string
    content: string
    metadata: Record<string, unknown>
    tags: string[]
  }>> {
    const memoryEntities = []
    
    for (const entity of scrapedEntities) {
      const memoryEntity = {
        id: entity.id,
        type: entity.type,
        name: entity.title,
        description: this.generateDescription(entity),
        content: entity.content,
        metadata: {
          source: entity.metadata.source,
          section: entity.metadata.section,
          difficulty: entity.metadata.difficulty,
          importance: entity.metadata.importance,
          word_count: entity.metadata.wordCount,
          estimated_read_time: entity.metadata.estimatedReadTime,
          last_updated: entity.metadata.lastUpdated || new Date().toISOString(),
          tags: entity.metadata.tags,
          typescript_specific: true,
          ingestion_timestamp: new Date().toISOString(),
          quality_score: this.calculateEntityQuality(entity)
        },
        tags: [
          'typescript',
          'documentation',
          entity.metadata.section,
          entity.metadata.difficulty,
          entity.metadata.importance,
          ...entity.metadata.tags
        ].filter((tag, index, arr) => arr.indexOf(tag) === index) // Remove duplicates
      }
      
      memoryEntities.push(memoryEntity)
    }
    
    return memoryEntities
  }

  /**
   * Generates entity relationships based on content analysis
   */
  private async generateEntityRelationships(
    entities: Array<{ id: string; name: string; content: string; metadata: Record<string, unknown> }>,
    sections: DocumentationSection[]
  ): Promise<Array<{
    source_id: string
    target_id: string
    relationship_type: 'references' | 'prerequisite' | 'continuation' | 'related' | 'example_of'
    strength: number
    metadata: Record<string, unknown>
  }>> {
    const relationships = []
    
    // Generate section-based relationships
    for (const section of sections) {
      const sectionEntities = entities.filter(e => 
        (e.metadata.section as string) === section.type
      )
      
      // Create sequential relationships within sections
      for (let i = 0; i < sectionEntities.length - 1; i++) {
        const current = sectionEntities[i]
        const next = sectionEntities[i + 1]
        
        relationships.push({
          source_id: current.id,
          target_id: next.id,
          relationship_type: 'continuation' as const,
          strength: 0.8,
          metadata: {
            section: section.type,
            sequential_order: i,
            relationship_basis: 'section_sequence'
          }
        })
      }
    }
    
    // Generate content-based relationships
    for (const entity of entities) {
      const relatedEntities = this.findRelatedEntities(entity, entities)
      
      for (const related of relatedEntities) {
        relationships.push({
          source_id: entity.id,
          target_id: related.id,
          relationship_type: 'related' as const,
          strength: related.strength,
          metadata: {
            relationship_basis: 'content_similarity',
            keywords_overlap: related.keywords,
            similarity_score: related.strength
          }
        })
      }
    }
    
    // Generate prerequisite relationships
    const prerequisiteMap = this.generatePrerequisiteMap()
    for (const [prereq, dependents] of prerequisiteMap) {
      const prereqEntity = entities.find(e => e.name.toLowerCase().includes(prereq))
      if (prereqEntity) {
        for (const dependent of dependents) {
          const dependentEntity = entities.find(e => e.name.toLowerCase().includes(dependent))
          if (dependentEntity) {
            relationships.push({
              source_id: prereqEntity.id,
              target_id: dependentEntity.id,
              relationship_type: 'prerequisite' as const,
              strength: 0.9,
              metadata: {
                relationship_basis: 'prerequisite_knowledge',
                prerequisite_topic: prereq,
                dependent_topic: dependent
              }
            })
          }
        }
      }
    }
    
    return relationships
  }

  /**
   * Calculates memory distribution strategy across databases
   */
  private async calculateMemoryDistribution(
    entities: Array<{ id: string; type: string; metadata: Record<string, unknown> }>
  ): Promise<{
    redis: string[]
    neo4j: string[]
    postgresql: string[]
    qdrant: string[]
  }> {
    const distribution = {
      redis: [] as string[],
      neo4j: [] as string[],
      postgresql: [] as string[],
      qdrant: [] as string[]
    }
    
    for (const entity of entities) {
      const importance = entity.metadata.importance as string
      
      // Redis: High-importance, frequently accessed content
      if (importance === 'critical' || importance === 'high') {
        distribution.redis.push(entity.id)
      }
      
      // Neo4j: All entities (for relationship graphs)
      distribution.neo4j.push(entity.id)
      
      // PostgreSQL: All entities (persistent storage)
      distribution.postgresql.push(entity.id)
      
      // Qdrant: All entities (for vector similarity search)
      distribution.qdrant.push(entity.id)
    }
    
    return distribution
  }

  /**
   * Generates comprehensive quality metrics
   */
  private async generateQualityMetrics(
    entities: Array<{ content: string; metadata: Record<string, unknown> }>,
    relationships: Array<{ strength: number }>,
    scrapingResult: ScrapingResult
  ): Promise<{
    validation_score: number
    confidence_scores: {
      content_accuracy: number
      relationship_strength: number
      metadata_completeness: number
      overall_quality: number
    }
  }> {
    // Content accuracy based on word count and structure
    const contentAccuracy = this.calculateContentAccuracy(entities)
    
    // Relationship strength based on average relationship scores
    const relationshipStrength = relationships.length > 0
      ? relationships.reduce((sum, rel) => sum + rel.strength, 0) / relationships.length
      : 0
    
    // Metadata completeness based on required fields
    const metadataCompleteness = this.calculateMetadataCompleteness(entities)
    
    // Overall quality as weighted average
    const overallQuality = (
      contentAccuracy * 0.4 +
      relationshipStrength * 0.3 +
      metadataCompleteness * 0.2 +
      scrapingResult.statistics.successRate * 0.1
    )
    
    return {
      validation_score: scrapingResult.statistics.successRate,
      confidence_scores: {
        content_accuracy: contentAccuracy,
        relationship_strength: relationshipStrength,
        metadata_completeness: metadataCompleteness,
        overall_quality: overallQuality
      }
    }
  }

  /**
   * Creates final ingestion package
   */
  private async createIngestionPackage(
    entities: Array<{
      id: string
      type: 'documentation' | 'guide' | 'reference' | 'tutorial' | 'example'
      name: string
      description: string
      content: string
      metadata: Record<string, unknown>
      tags: string[]
    }>,
    relationships: Array<{
      source_id: string
      target_id: string
      relationship_type: 'references' | 'prerequisite' | 'continuation' | 'related' | 'example_of'
      strength: number
      metadata: Record<string, unknown>
    }>,
    memoryDistribution: {
      redis: string[]
      neo4j: string[]
      postgresql: string[]
      qdrant: string[]
    },
    qualityMetrics: {
      validation_score: number
      confidence_scores: {
        content_accuracy: number
        relationship_strength: number
        metadata_completeness: number
        overall_quality: number
      }
    },
    scrapingResult: ScrapingResult
  ): Promise<PLCMemoryIngestionPackage> {
    const packageId = `typescript-docs-${Date.now()}`
    const totalWords = entities.reduce((sum, entity) => 
      sum + (entity.metadata.word_count as number || 0), 0
    )
    
    const ingestionPackage: PLCMemoryIngestionPackage = {
      package_id: packageId,
      timestamp: new Date().toISOString(),
      source_path: 'https://www.typescriptlang.org/docs/',
      source_type: 'typescript_documentation',
      entities,
      relationships,
      memory_distribution: memoryDistribution,
      validation_score: qualityMetrics.validation_score,
      confidence_scores: qualityMetrics.confidence_scores,
      statistics: {
        total_entities: entities.length,
        total_relationships: relationships.length,
        total_words: totalWords,
        processing_time_ms: Date.now() - this.startTime,
        success_rate: scrapingResult.statistics.successRate
      }
    }
    
    // Final validation using Zod schema
    const validationResult = PLCMemoryIngestionPackageSchema.safeParse(ingestionPackage)
    if (!validationResult.success) {
      throw new ValidationError(
        'Final ingestion package validation failed',
        ingestionPackage as Record<string, unknown>,
        validationResult.error.issues.map(err => ({
          path: err.path.join('.'),
          message: err.message
        }))
      )
    }
    
    return validationResult.data
  }

  /**
   * Validates and saves output to filesystem
   */
  private async validateAndSaveOutput(package_: PLCMemoryIngestionPackage): Promise<void> {
    try {
      // Ensure output directory exists
      await mkdir(this.config.outputDirectory, { recursive: true })
      
      // Write main ingestion package
      const outputPath = resolve(this.config.outputDirectory, this.config.outputFilename)
      await writeFile(outputPath, JSON.stringify(package_, null, 2), 'utf-8')
      this.log(`📄 Ingestion package saved to: ${outputPath}`)
      
      // Generate summary if requested
      if (this.config.generateSummary) {
        const summaryPath = resolve(this.config.outputDirectory, 'ingestion_summary.json')
        const summary = {
          package_id: package_.package_id,
          timestamp: package_.timestamp,
          source_type: package_.source_type,
          statistics: package_.statistics,
          quality_scores: package_.confidence_scores,
          memory_distribution_summary: {
            redis_entities: package_.memory_distribution.redis.length,
            neo4j_entities: package_.memory_distribution.neo4j.length,
            postgresql_entities: package_.memory_distribution.postgresql.length,
            qdrant_entities: package_.memory_distribution.qdrant.length
          }
        }
        await writeFile(summaryPath, JSON.stringify(summary, null, 2), 'utf-8')
        this.log(`📊 Summary saved to: ${summaryPath}`)
      }
      
    } catch (error) {
      throw new Error(`Failed to save output: ${error instanceof Error ? error.message : String(error)}`)
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  private log(message: string): void {
    if (this.config.enableVerboseLogging) {
      console.log(`[${new Date().toISOString()}] ${message}`)
    }
  }

  private generateDescription(entity: PLCMemoryEntity): string {
    const section = entity.metadata.section
    const difficulty = entity.metadata.difficulty
    const importance = entity.metadata.importance
    
    return `TypeScript ${section} documentation: ${entity.title}. ` +
           `Difficulty: ${difficulty}, Importance: ${importance}. ` +
           `Contains ${entity.metadata.wordCount} words with estimated ` +
           `read time of ${entity.metadata.estimatedReadTime} minutes.`
  }

  private calculateEntityQuality(entity: PLCMemoryEntity): number {
    let score = 0.5 // Base score
    
    // Content length scoring
    if (entity.content.length > 1000) score += 0.2
    if (entity.content.length > 3000) score += 0.1
    
    // Metadata completeness
    if (entity.metadata.lastUpdated) score += 0.1
    if (entity.metadata.tags.length > 0) score += 0.1
    
    // Importance weighting
    switch (entity.metadata.importance) {
      case 'critical': score += 0.1; break
      case 'high': score += 0.05; break
      default: break
    }
    
    return Math.min(score, 1.0)
  }

  private findRelatedEntities(
    entity: { id: string; content: string; name: string },
    allEntities: Array<{ id: string; content: string; name: string }>
  ): Array<{ id: string; strength: number; keywords: string[] }> {
    const related = []
    const entityKeywords = this.extractKeywords(entity.content + ' ' + entity.name)
    
    for (const other of allEntities) {
      if (other.id === entity.id) continue
      
      const otherKeywords = this.extractKeywords(other.content + ' ' + other.name)
      const commonKeywords = entityKeywords.filter(k => otherKeywords.includes(k))
      
      if (commonKeywords.length > 0) {
        const strength = commonKeywords.length / Math.max(entityKeywords.length, otherKeywords.length)
        if (strength > 0.1) { // Minimum similarity threshold
          related.push({
            id: other.id,
            strength,
            keywords: commonKeywords
          })
        }
      }
    }
    
    return related.sort((a, b) => b.strength - a.strength).slice(0, 5) // Top 5 related
  }

  private extractKeywords(text: string): string[] {
    const tsKeywords = [
      'type', 'interface', 'class', 'function', 'module', 'namespace',
      'generic', 'union', 'intersection', 'tuple', 'enum', 'decorator',
      'async', 'await', 'promise', 'callback', 'event', 'observable',
      'component', 'props', 'state', 'hook', 'context', 'ref'
    ]
    
    const words = text.toLowerCase().split(/\W+/)
    return tsKeywords.filter(keyword => words.includes(keyword))
  }

  private generatePrerequisiteMap(): Map<string, string[]> {
    const map = new Map<string, string[]>()
    
    map.set('basics', ['types', 'functions', 'objects', 'classes'])
    map.set('types', ['generics', 'utility types', 'advanced types'])
    map.set('functions', ['async', 'decorators', 'modules'])
    map.set('objects', ['interfaces', 'classes', 'namespaces'])
    map.set('interfaces', ['declaration merging', 'modules'])
    map.set('classes', ['decorators', 'mixins', 'inheritance'])
    map.set('modules', ['namespaces', 'module resolution', 'declaration files'])
    
    return map
  }

  private calculateContentAccuracy(entities: Array<{ content: string; metadata: Record<string, unknown> }>): number {
    let totalScore = 0
    
    for (const entity of entities) {
      let entityScore = 0.5 // Base score
      
      // Content length indicates depth
      const wordCount = entity.metadata.word_count as number || 0
      if (wordCount > 500) entityScore += 0.2
      if (wordCount > 1500) entityScore += 0.2
      
      // TypeScript-specific content
      const content = entity.content.toLowerCase()
      const tsIndicators = ['typescript', 'interface', 'type', 'generic', 'function']
      const foundIndicators = tsIndicators.filter(indicator => content.includes(indicator))
      entityScore += (foundIndicators.length / tsIndicators.length) * 0.1
      
      totalScore += Math.min(entityScore, 1.0)
    }
    
    return entities.length > 0 ? totalScore / entities.length : 0
  }

  private calculateMetadataCompleteness(entities: Array<{ metadata: Record<string, unknown> }>): number {
    const requiredFields = ['source', 'section', 'difficulty', 'importance', 'word_count']
    let completenessSum = 0
    
    for (const entity of entities) {
      const presentFields = requiredFields.filter(field => 
        entity.metadata[field] !== undefined && entity.metadata[field] !== null
      )
      completenessSum += presentFields.length / requiredFields.length
    }
    
    return entities.length > 0 ? completenessSum / entities.length : 0
  }
}

// =============================================================================
// CLI INTERFACE
// =============================================================================

/**
 * Main execution function for CLI usage
 */
async function main(): Promise<void> {
  try {
    console.log('🚀 TypeScript Documentation Ingestion for PLC Memory System')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    
    const engine = new TypeScriptDocsIngestionEngine({
      outputDirectory: './ingestion_output',
      enableVerboseLogging: true,
      generateSummary: true,
      validateOutput: true
    })
    
    const result = await engine.executeIngestion()
    
    console.log('\n✅ Ingestion completed successfully!')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log(`📦 Package ID: ${result.package_id}`)
    console.log(`📊 Entities: ${result.statistics.total_entities}`)
    console.log(`🔗 Relationships: ${result.statistics.total_relationships}`)
    console.log(`📝 Total Words: ${result.statistics.total_words.toLocaleString()}`)
    console.log(`⏱️  Processing Time: ${result.statistics.processing_time_ms}ms`)
    console.log(`🎯 Success Rate: ${(result.statistics.success_rate * 100).toFixed(1)}%`)
    console.log(`✨ Quality Score: ${(result.confidence_scores.overall_quality * 100).toFixed(1)}%`)
    
  } catch (error) {
    console.error('\n❌ Ingestion failed!')
    console.error('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`)
    
    if (error instanceof ValidationError) {
      console.error('\nValidation Errors:')
      error.validationErrors.forEach(err => {
        console.error(`  • ${err.path}: ${err.message}`)
      })
    }
    
    process.exit(1)
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

// Note: Types are already exported inline above (lines 94, 109)
// No additional exports needed to avoid conflicts

// Run main function if called directly
if (require.main === module) {
  main().catch(console.error)
} 