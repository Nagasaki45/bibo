var entriesList = new List(
    'entries',
    {valueNames: ['key', 'tag', 'author', 'year', 'title']}
);


function open_file(key) {
    var request = new XMLHttpRequest();
    request.open('GET', '/entry/' + key + '/open-file');
    request.send();
};


function fieldEdit(entryKey, field) {
    var id = '#' + entryKey + '-' + field;
    var previousValue = $(id).html();
    var input = null;
    if (field == 'review') {
        input = $('<textarea>' + previousValue + '</textarea>');
    } else {
        input = $('<input></input>')
            .attr({
                'type': 'text',
                'value': previousValue
            });
    }
    $(id).html('');
    $(input)
        .addClass('form-control')
        .on('blur', function() {
            $(id).html(this.value);
            $.post('/entry/' + entryKey + '/field-edit', {[field]: this.value});
        })
        .appendTo(id)
        .focus();
}


function fieldRemove(entryKey, field) {
    $('#' + entryKey + '-' + field).parent().remove();
    $.post('/entry/' + entryKey + '/field-remove', {field: field});
}
