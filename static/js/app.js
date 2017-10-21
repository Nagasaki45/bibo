var entriesList = new List(
    'entries',
    {valueNames: ['key', 'tag', 'author', 'year', 'title']}
);

function open_file(key) {
    var request = new XMLHttpRequest();
    request.open('GET', '/entry/' + key + '/open-file');
    request.send();
};
