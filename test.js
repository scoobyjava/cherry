function detectCircular(obj, seen = new WeakSet(), path = 'root') {
  if (obj && typeof obj === 'object') {
    if (seen.has(obj)) {
      console.log(`🔄 Circular reference detected at: ${path}`);
      return true;
    }
    seen.add(obj);
    for (let key in obj) {
      if (detectCircular(obj[key], seen, `${path}.${key}`)) {
        return true;
      }
    }
  }
  return false;
}

// Example usage:
const testObj = { a: {} };
testObj.a.b = testObj;

if (detectCircular(testObj)) {
  console.log('⚠️ Object contains circular references.');
} else {
  console.log('✅ No circular references detected.');
}
