import Docxtemplater from "docxtemplater";
import PizZip from "pizzip";
import PizZipUtils from "pizzip/utils/index.js";


function loadFile(url, callback) {
  PizZipUtils.getBinaryContent(url, callback);
}

function generate(url, data):Promise<string> {
  return new Promise(function (resolve, reject) {
    loadFile(url, function (error, content) {
      if (error) {
        throw error
      }
      ;

      // The error object contains additional information when logged with JSON.stringify (it contains a properties object containing all suberrors).
      function replaceErrors(key, value) {
        if (value instanceof Error) {
          return Object.getOwnPropertyNames(value).reduce(function (error, key) {
            error[key] = value[key];
            return error;
          }, {});
        }
        return value;
      }

      function errorHandler(error) {
        console.log(JSON.stringify({error: error}, replaceErrors));

        if (error.properties && error.properties.errors instanceof Array) {
          const errorMessages = error.properties.errors.map(function (error) {
            return error.properties.explanation;
          }).join("\n");
          console.log('errorMessages', errorMessages);
          // errorMessages is a humanly readable message looking like this :
          // 'The tag beginning with "foobar" is unopened'
        }
        throw error;
      }

      var zip = new PizZip(content);
      var doc;
      try {
        doc = new Docxtemplater(zip, {parser: angularParser});
      } catch (error) {
        // Catch compilation errors (errors caused by the compilation of the template : misplaced tags)
        errorHandler(error);
      }

      doc.setData(data);
      try {
        // render the document (replace all occurences of {first_name} by John, {last_name} by Doe, ...)
        doc.render();
      } catch (error) {
        // Catch rendering errors (errors relating to the rendering of the template : angularParser throws an error)
        errorHandler(error);
      }

      resolve(doc.getZip().generate({
        type: "blob",
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })) //Output the document using Data-URI

    })
  })

}

// Please make sure to use angular-expressions 1.0.1 or later
// More detail at https://github.com/open-xml-templating/docxtemplater/issues/488
let expressions = require('angular-expressions');
let assign = require("lodash/assign");
// define your filter functions here, for example, to be able to write {clientname | lower}
expressions.filters.russian_date = function (input) {
  // This condition should be used to make sure that if your input is
  // undefined, your output will be undefined as well and will not
  // throw an error
  if (!input) return input;
  let options = {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    timezone: 'UTC'
  };
  input = new Date(input);
  return input.toLocaleString("ru", options);
}

function angularParser(tag) {
  if (tag === '.') {
    return {
      get: function (s) {
        return s;
      }
    };
  }
  const expr = expressions.compile(
    tag.replace(/(’|‘)/g, "'").replace(/(“|”)/g, '"')
  );
  return {
    get: function (scope, context) {
      let obj = {};
      const scopeList = context.scopeList;
      const num = context.num;
      for (let i = 0, len = num + 1; i < len; i++) {
        obj = assign(obj, scopeList[i]);
      }
      return expr(scope, obj);
    }
  };
}

export {generate}
