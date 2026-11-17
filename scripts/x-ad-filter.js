/* Experimental Loon response filter, 2026-11-17.
 * No telemetry, networking, persistence, or changes to routing.
 * Requires decryptable JSON GraphQL responses; not tested against the user's app.
 */
(function () {
  'use strict';
  var output = {};
  var removed = 0;
  var visited = 0;
  var supported = /^https:\/\/(?:api\.)?(?:twitter\.com|x\.com)\/(?:i\/api\/)?graphql\/[^/?]+\/(?:HomeTimeline|HomeLatestTimeline|SearchTimeline|TweetDetail|UserTweets|UserTweetsAndReplies|ListLatestTweetsTimeline)(?:[/?]|$)/i;
  function object(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }
  function metadata(value) {
    return object(value) && object(value.promotedMetadata) && Object.keys(value.promotedMetadata).length > 0;
  }
  function isPromoted(value) {
    if (!object(value)) return false;
    if (typeof value.entryId === 'string' && /^promoted-tweet-/.test(value.entryId)) return true;
    var content = object(value.content) ? value.content : {};
    var item = object(value.item) ? value.item : {};
    return metadata(value) || metadata(value.itemContent) || metadata(content.itemContent) || metadata(item.itemContent);
  }
  function walk(value, depth) {
    if (++visited > 60000 || depth > 90) throw new Error('budget');
    if (Array.isArray(value)) {
      for (var i = 0; i < value.length; i++) walk(value[i], depth + 1);
    } else if (object(value)) {
      Object.keys(value).forEach(function (key) {
        var child = value[key];
        if ((key === 'entries' || key === 'items') && Array.isArray(child)) {
          value[key] = child.filter(function (entry) {
            if (!isPromoted(entry)) return true;
            removed++;
            return false;
          });
          child = value[key];
        }
        walk(child, depth + 1);
      });
    }
  }
  try {
    var request = typeof $request === 'undefined' ? {} : $request;
    var response = typeof $response === 'undefined' ? {} : $response;
    if (supported.test(request.url || '') && Number(response.status) === 200 &&
        typeof response.body === 'string' && response.body.length <= 3 * 1024 * 1024) {
      var data = JSON.parse(response.body);
      if (object(data) && object(data.data) && !data.errors) {
        walk(data.data, 0);
        if (removed > 0) output = {body: JSON.stringify(data)};
        console.log('[X-AdFilter] JSON processed; promoted entries removed: ' + removed);
      }
    }
  } catch (_) {
    output = {};
    console.log('[X-AdFilter] Unsupported response; passed through unchanged.');
  }
  $done(output);
}());
