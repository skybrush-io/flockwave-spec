import { compileFromFile } from "json-schema-to-typescript";
import { promises as fsPromises } from "node:fs";
import { join } from "node:path";
import { chdir } from "node:process";

chdir(join(import.meta.dirname, "..", ".."));

const SPEC_DIR = "./src/flockwave/spec";
const OUTPUT_DIR = "./types";

const getSingleNonNullTypeFromSchema = (schema) => {
  const nonNullTypes = Array.isArray(schema.type)
    ? schema.type.filter((t) => t !== "null")
    : [schema.type];
  return nonNullTypes.length === 1 ? nonNullTypes[0] : null;
};

const shouldPreventSeparateType = (schema) => {
  if (!schema.title) {
    return false;
  }

  const title = schema.title.toLowerCase();

  // Always generate a separate type if the title ends with "ID" (case-insensitive)
  // because it is likely to be a unique identifier
  if (title.endsWith(" id")) {
    return false;
  }

  const type = getSingleNonNullTypeFromSchema(schema);
  if (type) {
    // Never generate a separate type name for booleans, numbers or integers
    if (type === "boolean" || type === "number" || type === "integer") {
      return true;
    }

    // If the type is "string", generate a separate type only if it is an enum
    if (type === "string") {
      return !schema.enum;
    }

    // If the type is "array" and the items contains a ref to another type only, do not generate a separate type for the array itself
    if (
      type === "array" &&
      schema.items &&
      typeof getSingleNonNullTypeFromSchema(schema.items) === "string"
    ) {
      return true;
    }
  }

  // In all other cases, do not prevent the generation of a separate type
  return false;
};

const result = await compileFromFile(`${SPEC_DIR}/message.json`, {
  cwd: SPEC_DIR,
  customName: (schema, key) => {
    // For some simple cases, prevent the generation of a separate type even if we
    // have a title (which is a human-readable label)
    if (shouldPreventSeparateType(schema)) {
      delete schema.title;
      return undefined;
    }

    // Prefer $id over the title of the schema because the title is meant to be
    // human-readable.
    //
    // We can also include $tsType later if needed
    return schema.$id || key;
  },
});

await fsPromises.writeFile(`${OUTPUT_DIR}/index.d.ts`, result);
