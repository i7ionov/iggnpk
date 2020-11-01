import {arrayDifference} from './arrayDifference'
import {objectDifference} from './objectDifference'

let quickDiffTresholdDefault = false
function setQuickDiffTresholdDefault(treshold) {
  quickDiffTresholdDefault=treshold
}
const getDifference = (a, b, options?) => {
  let quickDiffTreshold = options&&options.quickDiffTreshold?options.quickDiffTreshold:quickDiffTresholdDefault

  if (a === b) {
    return undefined
  } else if (a instanceof Array && b instanceof Array) {
    return arrayDifference(a, b, {
      comparisonFunction: getDifference,
      quickDiffTreshold: quickDiffTreshold
    })
  } else if (a instanceof Object && b instanceof Object) {
    return objectDifference(a, b, {
      comparisonFunction: getDifference,
      quickDiffTreshold: quickDiffTreshold
    })
  }
  else {
    return [a, b]
  }
}

export { getDifference, setQuickDiffTresholdDefault }
