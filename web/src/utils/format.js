import { date } from "quasar";

// dropdown options formatting

function _formatOptions(data, { label, value = "id", flat = false, allowDuplicates = true }) {
  if (!flat)
    // returns array of options in object format [{label: label, value: 1}]
    return data.map(i => ({ label: i[label], value: i[value] }));
  else
    // returns options as an array of strings ["label", "label1"]
    if (!allowDuplicates)
      return data.map(i => i[label]);
    else {
      const options = []
      data.forEach(i => {
        if (!options.includes(i[label]))
          options.push(i[label])
      });
      return options
    }
}

export function formatScriptOptions(data, flat = false) {
  if (flat) {
    // returns just script names in array
    return _formatOptions(data, { label: "name", value: "pk", flat: true, allowDuplicates: false })
  } else {

    let options = [];
    let categories = [];
    let create_unassigned = false
    data.forEach(script => {
      if (!!script.category && !categories.includes(script.category)) {
        categories.push(script.category);
      } else if (!script.category) {
        create_unassigned = true
      }
    });

    if (create_unassigned) categories.push("Unassigned")

    categories.sort().forEach(cat => {
      options.push({ category: cat });
      let tmp = [];
      data.forEach(script => {
        if (script.category === cat) {
          tmp.push({ label: script.name, value: script.id, timeout: script.default_timeout, args: script.args, filename: script.filename, syntax: script.syntax });
        } else if (cat === "Unassigned" && !script.category) {
          tmp.push({ label: script.name, value: script.id, timeout: script.default_timeout, args: script.args, filename: script.filename, syntax: script.syntax });
        }
      })
      const sorted = tmp.sort((a, b) => a.label.localeCompare(b.label));
      options.push(...sorted);
    });

    return options;
  }
}

export function formatAgentOptions(data, flat = false, value_field = "agent_id") {

  if (flat) {
    // returns just agent hostnames in array
    return _formatOptions(data, { label: "hostname", value: value_field, flat: true, allowDuplicates: false })
  } else {
    // returns options with categories in object format
    let options = []
    const agents = data.map(agent => ({
      label: agent.hostname,
      value: agent[value_field],
      cat: `${agent.client} > ${agent.site}`,
    }));

    let categories = [];
    agents.forEach(option => {
      if (!categories.includes(option.cat)) {
        categories.push(option.cat);
      }
    });

    categories.sort().forEach(cat => {
      options.push({ category: cat });
      let tmp = []
      agents.forEach(agent => {
        if (agent.cat === cat) {
          tmp.push(agent);
        }
      });

      const sorted = tmp.sort((a, b) => a.label.localeCompare(b.label));
      options.push(...sorted);
    });

    return options
  }
}

export function formatCustomFieldOptions(data, flat = false) {
  if (flat) {
    return _formatOptions(data, { label: "name", flat: true })
  }
  else {
    const categories = ["Client", "Site", "Agent"]
    const options = []

    categories.forEach(cat => {
      options.push({ category: cat });
      const tmp = [];
      data.forEach(custom_field => {
        if (custom_field.model === cat.toLowerCase()) {
          tmp.push({ label: custom_field.name, value: custom_field.id })
        }
      });

      const sorted = tmp.sort((a, b) => a.label.localeCompare(b.label));
      options.push(...sorted);
    })

    return options
  }
}

export function formatClientOptions(data, flat = false) {
  return _formatOptions(data, { label: "name", flat: flat })
}

export function formatSiteOptions(data, flat = false) {
  const options = []

  data.forEach(client => {
    options.push({ category: client.name });
    options.push(..._formatOptions(client.sites, { label: "name", flat: flat }))
  });

  return options
}

export function formatUserOptions(data, flat = false) {
  return _formatOptions(data, { label: "username", flat: flat })
}

export function formatCheckOptions(data, flat = false) {
  return _formatOptions(data, { label: "readable_desc", flat: flat })
}


export function formatCustomFields(fields, values) {
  let tempArray = [];

  for (let field of fields) {
    if (field.type === "multiple") {
      tempArray.push({ multiple_value: values[field.name], field: field.id });
    } else if (field.type === "checkbox") {
      tempArray.push({ bool_value: values[field.name], field: field.id });
    } else {
      tempArray.push({ string_value: values[field.name], field: field.id });
    }
  }
  return tempArray
}

export function formatScriptSyntax(syntax) {
  let temp = syntax
  temp = temp.replaceAll("<", "&lt;").replaceAll(">", "&gt;")
  temp = temp.replaceAll("&lt;", `<span style="color:#d4d4d4">&lt;</span>`).replaceAll("&gt;", `<span style="color:#d4d4d4">&gt;</span>`)
  temp = temp.replaceAll("[", `<span style="color:#ffd70a">[</span>`).replaceAll("]", `<span style="color:#ffd70a">]</span>`)
  temp = temp.replaceAll("(", `<span style="color:#87cefa">(</span>`).replaceAll(")", `<span style="color:#87cefa">)</span>`)
  temp = temp.replaceAll("{", `<span style="color:#c586b6">{</span>`).replaceAll("}", `<span style="color:#c586b6">}</span>`)
  temp = temp.replaceAll("\n", `<br />`)
  return temp
}

// date formatting

export function formatDate(dateString) {
  if (!dateString) return "";
  const d = date.extractDate(dateString, "MM DD YYYY HH:mm");
  return date.formatDate(d, "MMM-DD-YYYY - HH:mm");
}

export function getNextAgentUpdateTime() {
  const d = new Date();
  let ret;
  if (d.getMinutes() <= 35) {
    ret = d.setMinutes(35);
  } else {
    ret = date.addToDate(d, { hours: 1 });
    ret.setMinutes(35);
  }
  const a = date.formatDate(ret, "MMM D, YYYY");
  const b = date.formatDate(ret, "h:mm A");
  return `${a} at ${b}`;
}

export function dateStringToUnix(drfString) {
  if (!drfString) return 0;
  const d = date.extractDate(drfString, "MM DD YYYY HH:mm");
  return parseInt(date.formatDate(d, "X"));
}

// string formatting

export function capitalize(string) {
  return string[0].toUpperCase() + string.substring(1);
}

export function formatTableColumnText(text) {

  let string = ""
  // split at underscore if exists
  const words = text.split("_")
  words.forEach(word => string = string + " " + capitalize(word))

  return string.trim()
}

export function truncateText(txt, chars) {
  if (!txt) return

  return txt.length >= chars ? txt.substring(0, chars) + "..." : txt;
}

export function bytes2Human(bytes) {
  if (bytes == 0) return "0B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

export function convertMemoryToPercent(percent, memory) {
  const mb = memory * 1024;
  return Math.ceil((percent * mb) / 100).toLocaleString();
}
