// mini-schema: a keyword-exact JSON Schema (draft 2020-12 subset) validator
// for the T-005 results/ schemas, used by prebuild-data.mjs so the web build
// needs no new npm dependency (ajv would be a dependency decision for Mico;
// the keyword set of the three results/ schemas is closed and small).
// Any keyword this file does not implement THROWS, so a future schema keyword
// can never silently bypass validation - extend here explicitly instead.
//
// Implemented: type, properties, required, additionalProperties (boolean),
// items, minItems, minLength, minimum, pattern, enum, const, anyOf, allOf,
// if/then/else. Annotations ($schema, $id, title, description, examples,
// default) are ignored. Boolean schemas (true/false) are honored.

const ANNOTATIONS = new Set(["$schema", "$id", "title", "description", "examples", "default"]);
const IMPLEMENTED = new Set([
  "type",
  "properties",
  "required",
  "additionalProperties",
  "items",
  "minItems",
  "minLength",
  "minimum",
  "pattern",
  "enum",
  "const",
  "anyOf",
  "allOf",
  "if",
  "then",
  "else",
]);

function checkKeywords(schema, where) {
  if (schema === true || schema === false) return;
  if (schema === null || typeof schema !== "object" || Array.isArray(schema)) {
    throw new Error(`mini-schema: ${where}: subschema must be an object or boolean`);
  }
  for (const k of Object.keys(schema)) {
    if (!IMPLEMENTED.has(k) && !ANNOTATIONS.has(k)) {
      throw new Error(
        `mini-schema: ${where}: unsupported keyword "${k}" - extend web/scripts/mini-schema.mjs, never bypass`,
      );
    }
  }
}

function typeOk(instance, type) {
  switch (type) {
    case "object":
      return typeof instance === "object" && instance !== null && !Array.isArray(instance);
    case "array":
      return Array.isArray(instance);
    case "string":
      return typeof instance === "string";
    case "number":
      return typeof instance === "number" && Number.isFinite(instance);
    case "integer":
      return typeof instance === "number" && Number.isInteger(instance);
    case "boolean":
      return typeof instance === "boolean";
    case "null":
      return instance === null;
    default:
      throw new Error(`mini-schema: unsupported type "${type}"`);
  }
}

function deepEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function describe(instance) {
  if (instance === null) return "null";
  if (Array.isArray(instance)) return "array";
  return typeof instance === "string" ? JSON.stringify(instance) : String(instance);
}

// Returns an array of error messages (empty = valid). Throws on unsupported
// schema keywords (see checkKeywords) - callers must not swallow that.
export function validate(instance, schema, where = "$") {
  checkKeywords(schema, where);
  const errors = [];
  if (schema === true) return errors;
  if (schema === false) {
    errors.push(`${where}: false schema matches nothing`);
    return errors;
  }
  if (schema.type !== undefined) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.some((t) => typeOk(instance, t))) {
      errors.push(`${where}: expected type ${types.join("|")}, got ${describe(instance)}`);
    }
  }
  if (schema.const !== undefined && !deepEqual(instance, schema.const)) {
    errors.push(`${where}: expected const ${JSON.stringify(schema.const)}, got ${describe(instance)}`);
  }
  if (schema.enum !== undefined && !schema.enum.some((v) => deepEqual(instance, v))) {
    errors.push(`${where}: ${describe(instance)} not in enum ${JSON.stringify(schema.enum)}`);
  }
  if (typeof instance === "string") {
    if (schema.minLength !== undefined && instance.length < schema.minLength) {
      errors.push(`${where}: string shorter than minLength ${schema.minLength}`);
    }
    if (schema.pattern !== undefined && !new RegExp(schema.pattern).test(instance)) {
      errors.push(`${where}: ${describe(instance)} does not match pattern ${schema.pattern}`);
    }
  }
  if (typeof instance === "number") {
    if (schema.minimum !== undefined && instance < schema.minimum) {
      errors.push(`${where}: ${instance} < minimum ${schema.minimum}`);
    }
  }
  if (Array.isArray(instance)) {
    if (schema.minItems !== undefined && instance.length < schema.minItems) {
      errors.push(`${where}: array shorter than minItems ${schema.minItems}`);
    }
    if (schema.items !== undefined) {
      instance.forEach((item, i) => errors.push(...validate(item, schema.items, `${where}[${i}]`)));
    }
  }
  if (typeof instance === "object" && instance !== null && !Array.isArray(instance)) {
    if (schema.required !== undefined) {
      for (const key of schema.required) {
        if (!(key in instance)) errors.push(`${where}: missing required field "${key}"`);
      }
    }
    if (schema.properties !== undefined) {
      for (const [key, subschema] of Object.entries(schema.properties)) {
        if (key in instance) errors.push(...validate(instance[key], subschema, `${where}.${key}`));
      }
    }
    if (schema.additionalProperties === false && schema.properties !== undefined) {
      for (const key of Object.keys(instance)) {
        if (!(key in schema.properties)) {
          errors.push(`${where}: unexpected field "${key}" (additionalProperties: false)`);
        }
      }
    }
  }
  if (schema.anyOf !== undefined) {
    const matched = schema.anyOf.some((branch) => validate(instance, branch, where).length === 0);
    if (!matched) {
      errors.push(`${where}: matched none of anyOf (${schema.anyOf.length} branches)`);
    }
  }
  if (schema.allOf !== undefined) {
    schema.allOf.forEach((branch, i) =>
      errors.push(...validate(instance, branch, `${where}(allOf[${i}])`)),
    );
  }
  if (schema.if !== undefined) {
    const ifOk = validate(instance, schema.if, where).length === 0;
    if (ifOk && schema.then !== undefined) {
      errors.push(...validate(instance, schema.then, `${where}(then)`));
    } else if (!ifOk && schema.else !== undefined) {
      errors.push(...validate(instance, schema.else, `${where}(else)`));
    }
  }
  return errors;
}
