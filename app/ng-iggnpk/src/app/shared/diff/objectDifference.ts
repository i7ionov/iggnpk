let getKeys = function(o) {
  if (o instanceof Map) {
    var mapKeys = [];
    o.forEach((value,key) => {
      mapKeys.push(key);
    });
    return mapKeys;
  }
  return Object.keys(o);
};

let hasOwnProperty = function(o, key) {
  var keys = getKeys(o);
  return getKeys(o).indexOf(key)!=-1;
};

const keysUnion = (a, b) =>
    getKeys(a)
        .concat(
        getKeys(b)
            .filter(key => !hasOwnProperty(a,key)))

const REMOVED = 0
const KEPT = 1
const ADDED = 2

const annotateKey = (a, b) => key => ({
  key,
  status: (() => {
    if (hasOwnProperty(a, key) && !hasOwnProperty(b, key)) {
      return REMOVED
    }
    if (hasOwnProperty(a, key) && hasOwnProperty(b, key)) {
      return KEPT
    }
    if (!hasOwnProperty(a, key) && hasOwnProperty(b, key)) {
      return ADDED
    }
  })(),
  value: [
    a[key],
    b[key]
  ]
})

const LEFT = 0
const RIGHT = 1

const POSITION_FOR_SIDE = {
  [LEFT]: REMOVED,
  [RIGHT]: ADDED
}

const reduceSide = (side, options) => (object, annotatedKey) => {
  switch (annotatedKey.status) {
    case POSITION_FOR_SIDE[side]:
      object[annotatedKey.key] = annotatedKey.value[side]
      break

    case KEPT:
      const comparisonResult = options.comparisonFunction(
          annotatedKey.value[LEFT],
          annotatedKey.value[RIGHT],
          options
      )

      if (comparisonResult != null) {
        object[annotatedKey.key] = comparisonResult[side]
      }
      break
  }

  return object
}

const QUICKDIFF_INDICE = '_QUICKDIFF_'

const objectDifference = (a, b, options) => {
  var mapToObject = function(map) {
    if (map instanceof Map) {
      let obj = {};
      if (options.quickDiffTreshold && map.size>options.quickDiffTreshold) {
        // quick diff based on map length
        obj[QUICKDIFF_INDICE]=map.size
      }
      else {
        // full diff based on map entries
        map.forEach((value, key) => {
          obj[key] = mapToObject(value);
        });
      }
      return obj
    }

    else if (map instanceof Object) {
      let result = {};
      if (options.quickDiffTreshold && Object.keys(map).length>options.quickDiffTreshold) {
        // quick diff based on object length
        result[QUICKDIFF_INDICE] = Object.keys(map).length
      }
      else {
        // full diff based on object keys
        Object.keys(map).forEach(key => {
          result[key] = mapToObject(map[key])
        })
      }
      return result;
    }
    return map
  }

  a = mapToObject(a)
  b = mapToObject(b)

  const result = [LEFT, RIGHT].map(side =>
      keysUnion(a, b)
          .map(annotateKey(a, b))
          .reduce(reduceSide(side, options), {}))
      .map(side =>
          getKeys(side).length > 0
              ? side
              : undefined)
  return result[LEFT] === undefined && result[RIGHT] === undefined
      ? undefined
      : result
}

export { objectDifference }
