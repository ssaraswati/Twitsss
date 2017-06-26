/**
 * Map function - use `emit(key, value)1 to generate rows in the output result.
 * @link http://docs.couchdb.org/en/latest/couchapp/ddocs.html#reduce-and-rereduce-functions
 *
 * @param {object} doc - Document Object.
 */
function(doc) {
    if (doc.type === "tweet" && (doc.latitude != null && doc.longitude != null)){
        emit(['Aus',doc.city,doc._id], 1)
    }

}

