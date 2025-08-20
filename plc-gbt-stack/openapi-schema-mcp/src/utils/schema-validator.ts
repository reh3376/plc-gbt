/**
 * OpenAPI Schema Validator
 * Validates data against OpenAPI schemas using AJV
 */

import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { OpenAPISchema } from './schema-store.js';

export interface ValidationResult {
  valid: boolean;
  errors?: any[];
  data?: any;
}

export class SchemaValidator {
  private ajv: Ajv;
  
  constructor() {
    this.ajv = new Ajv({ 
      strict: false,
      allErrors: true,
      coerceTypes: false
    });
    
    // Add format validators
    addFormats(this.ajv);
    
    // Add custom formats
    this.ajv.addFormat('uuid', /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
  }

  /**
   * Compile OpenAPI schema into AJV validator
   */
  public compileSchema(schema: OpenAPISchema): void {
    // Add component schemas first
    if (schema.components?.schemas) {
      Object.entries(schema.components.schemas).forEach(([name, schemaDefinition]) => {
        const schemaId = `#/components/schemas/${name}`;
        this.ajv.addSchema(schemaDefinition, schemaId);
      });
    }

    // Add parameter schemas
    if (schema.components?.parameters) {
      Object.entries(schema.components.parameters).forEach(([name, paramDefinition]) => {
        const schemaId = `#/components/parameters/${name}`;
        this.ajv.addSchema(paramDefinition, schemaId);
      });
    }
  }

  /**
   * Validate data against a schema reference
   */
  public validate(schemaRef: string, data: any): ValidationResult {
    try {
      const validate = this.ajv.getSchema(schemaRef);
      
      if (!validate) {
        return {
          valid: false,
          errors: [{ message: `Schema not found: ${schemaRef}` }]
        };
      }

      const valid = validate(data);
      
      return {
        valid: !!valid,
        errors: validate.errors || undefined,
        data: valid ? data : undefined
      };
    } catch (error) {
      return {
        valid: false,
        errors: [{ message: error instanceof Error ? error.message : 'Validation error' }]
      };
    }
  }

  /**
   * Validate request body against OpenAPI operation
   */
  public validateRequest(
    operation: any,
    data: any
  ): ValidationResult {
    if (!operation.requestBody?.content?.['application/json']?.schema) {
      return { valid: true, data }; // No schema to validate against
    }

    const schema = operation.requestBody.content['application/json'].schema;
    
    // Handle $ref
    if (schema.$ref) {
      return this.validate(schema.$ref, data);
    }

    // Inline schema
    const validateFn = this.ajv.compile(schema);
    const valid = validateFn(data);
    
    return {
      valid: !!valid,
      errors: validateFn.errors || undefined,
      data: valid ? data : undefined
    };
  }

  /**
   * Validate response against OpenAPI operation
   */
  public validateResponse(
    operation: any,
    statusCode: number,
    data: any
  ): ValidationResult {
    const response = operation.responses?.[statusCode.toString()];
    
    if (!response?.content?.['application/json']?.schema) {
      return { valid: true, data }; // No schema to validate against
    }

    const schema = response.content['application/json'].schema;
    
    // Handle $ref
    if (schema.$ref) {
      return this.validate(schema.$ref, data);
    }

    // Inline schema
    const validateFn = this.ajv.compile(schema);
    const valid = validateFn(data);
    
    return {
      valid: !!valid,
      errors: validateFn.errors || undefined,
      data: valid ? data : undefined
    };
  }

  /**
   * Get compiled validator function for reuse
   */
  public getValidator(schemaRef: string) {
    return this.ajv.getSchema(schemaRef);
  }

  /**
   * Clear all compiled schemas
   */
  public clearSchemas(): void {
    this.ajv.removeSchema();
  }
}
