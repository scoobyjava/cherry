async function routeUserRequest(request, agentExecutor) {
  const tasks = [];

  // If a text part exists, route it to the NLP agent
  if (request.text) {
    tasks.push(
      agentExecutor('nlp-agent', { text: request.text })
        .then(result => ({ type: 'text', result }))
    );
  }

  // If an image part exists, route it to the vision analysis agent
  if (request.image) {
    tasks.push(
      agentExecutor('vision-agent', { image: request.image })
        .then(result => ({ type: 'image', result }))
    );
  }

  // If an audio part exists, route it to the audio analysis agent
  if (request.audio) {
    tasks.push(
      agentExecutor('audio-agent', { audio: request.audio })
        .then(result => ({ type: 'audio', result }))
    );
  }

  const results = await Promise.all(tasks);
  return mergeResults(results);
}

function mergeResults(results) {
  // Combine the individual agent responses.
  // The merging logic can be customized based on application requirements.
  const merged = {};
  results.forEach(res => {
    merged[res.type] = res.result;
  });
  return merged;
}

module.exports = { routeUserRequest };
