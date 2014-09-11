/*global define, require */
/**
 * To load this extension, add the following to your custom.js:
 *
 * $([IPython.events]).on('app_initialized.NotebookApp', function() {
 *     require(['nbextensions/assignment'], function (assignment) {
 *         console.log('Assignment extension loaded');
 *         assignment.register(IPython.notebook);
 *         // Optional: uncomment this line if you always want to display
 *         // the notebook based on the assignment metadata, even if the
 *         // toolbar isn't activated. This has the effect of coloring
 *         // gradeable and autograder cells.
 *         //assignment.display(IPython.notebook);
 *     });
 * });
 *
**/

define([
    'base/js/namespace',
    'jquery',
    'notebook/js/celltoolbar',

], function (IPython, $, celltoolbar) {
    "use strict";

    var CellToolbar = celltoolbar.CellToolbar;

    /**
     * Get the assignment cell type. Default is "-".
     */
    var get_cell_type = function (cell) {
        if (cell.metadata.assignment === undefined) {
            return '-';
        } else {
            return cell.metadata.assignment.cell_type;
        }
    };

    /**
     * Add a display class to the cell element, depending on the
     * assignment cell type.
     */
    var display_cell_type = function (cell) {
        var cell_type = get_cell_type(cell),
            grade_cls = "assignment-gradeable-cell",
            test_cls = "assignment-autograder-cell",
            elem = cell.element;

        if (!elem) {
            return;
        }

        if (cell_type === "grade" && !elem.hasClass(grade_cls)) {
            elem.addClass(grade_cls);
        } else if (cell_type !== "grade" && elem.hasClass(grade_cls)) {
            elem.removeClass(grade_cls);
        }

        if (cell_type === "autograder" && !elem.hasClass(test_cls)) {
            elem.addClass(test_cls);
            if (IPython.notebook.metadata.hide_autograder_cells) {
                elem.hide();
            }
        } else if (cell_type !== "autograder" && elem.hasClass(test_cls)) {
            elem.removeClass(test_cls);
        }
    };

    /**
     * Create a select drop down menu for the assignment cell type. On
     * change, this rebuilds the cell toolbar so that other elements
     * may (possibly) be displayed -- for example, "grade" cells need
     * input text boxes for the problem id and points.
     */
    var create_type_select = function (div, cell, celltoolbar) {
        var list_list = [
            ['-'             , '-'         ],
            ['To be graded'  , 'grade'     ],
            ['Release only'  , 'release'   ],
            ['Solution only' , 'solution'  ],
            ['Skip'          , 'skip'      ],
            ['Autograder'    , 'autograder'],
        ];

        var local_div = $('<div/>');
        var select = $('<select/>');
        for(var i=0; i < list_list.length; i++){
            var opt = $('<option/>')
                    .attr('value', list_list[i][1])
                    .text(list_list[i][0]);
            select.append(opt);
        }

        select.addClass('assignment-type-select');
        select.val(get_cell_type(cell));
        select.change(function () {
            cell.metadata.assignment.cell_type = select.val();
            celltoolbar.rebuild();
            display_cell_type(cell);
        });

        local_div.addClass('assignment-type');
        $(div).append(local_div.append($('<span/>').append(select)));
    };

    /**
     * Create the input text box for the problem or test id.
     */
    var create_id_input = function (div, cell, celltoolbar) {
        var local_div = $('<div/>');
        var text = $('<input/>').attr('type', 'text');
        var lbl;
        if (get_cell_type(cell) === 'grade') {
            lbl = $('<label/>').append($('<span/>').text('Problem ID: '));
        } else {
            lbl = $('<label/>').append($('<span/>').text('Test name: '));
        }
        lbl.append(text);

        text.addClass('assignment-id-input');
        text.attr("value", cell.metadata.assignment.id);
        text.keyup(function () {
            cell.metadata.assignment.id = text.val();
        });
                
        local_div.addClass('assignment-id');
        $(div).append(local_div.append($('<span/>').append(lbl)));

        IPython.keyboard_manager.register_events(text);
    };

    /**
     * Create the input text box for the number of points the problem
     * is worth.
     */
    var create_points_input = function (div, cell, celltoolbar) {
        var local_div = $('<div/>');
        var text = $('<input/>').attr('type', 'text');
        var lbl = $('<label/>').append($('<span/>').text('Points: '));
        lbl.append(text);

        text.addClass('assignment-points-input');
        text.attr("value", cell.metadata.assignment.points);
        text.keyup(function () {
            cell.metadata.assignment.points = text.val();
        });

        local_div.addClass('assignment-points');
        $(div).append(local_div.append($('<span/>').append(lbl)));

        IPython.keyboard_manager.register_events(text);
    };

    /**
     * Create the input text box for the autograder test weight.
     */
    var create_weight_input = function (div, cell, celltoolbar) {
        var local_div = $('<div/>');
        var text = $('<input/>').attr('type', 'text');
        var lbl = $('<label/>').append($('<span/>').text('Weight: '));
        lbl.append(text);

        text.addClass('assignment-weight-input');
        text.attr("value", cell.metadata.assignment.weight);
        text.keyup(function () {
            cell.metadata.assignment.weight = text.val();
        });

        local_div.addClass('assignment-weight');
        $(div).append(local_div.append($('<span/>').append(lbl)));

        IPython.keyboard_manager.register_events(text);
    };

    /**
     * Create the cell toolbar assignment element, which will include
     * different subelements depending on what the assignment cell
     * type is.
     */
    var assignment = function (div, cell, celltoolbar) {
        var button_container = $(div);
        button_container.addClass('assignment-controls');

        // create the metadata dictionary if it doesn't exist
        if (!cell.metadata.assignment) {
            cell.metadata.assignment = {};
        }

        var cell_type = get_cell_type(cell);

        if (cell_type === 'grade') {
            // grade cells need the id input box and points input box
            create_id_input(div, cell, celltoolbar);
            create_points_input(div, cell, celltoolbar);
            
        } else if (cell_type === 'autograder') {
            // autograder cells need the id input box and weight input box
            create_id_input(div, cell, celltoolbar);
            create_weight_input(div, cell, celltoolbar);
        }

        // all cells get the cell type dropdown menu
        create_type_select(div, cell, celltoolbar);
    };

    /**
     * Load custom css for the assignment toolbar.
     */
    var load_css = function () {
        var link = document.createElement('link');
        link.type = 'text/css';
        link.rel = 'stylesheet';
        link.href = '/nbextensions/assignment.css';
        console.log(link);
        document.getElementsByTagName('head')[0].appendChild(link);
    };

    /**
     * Load the assignment toolbar extension.
     */
    var register = function (notebook) {
        load_css();

        var metadata = IPython.notebook.metadata;
        if (!metadata.disable_assignment_toolbar) {
            CellToolbar.register_callback('create_assignment.assignment', assignment);
            CellToolbar.register_preset('Create Assignment', ['create_assignment.assignment'], notebook);
            console.log('Assignment extension for metadata editing loaded.');
        }
    };

    /**
     * Display cells appropriately depending on whether they're
     * gradeable, etc.
     */
    var display = function (notebook) {
        var cells = notebook.get_cells();
        for (var i = 0; i < cells.length; i++) {
            display_cell_type(cells[i]);
        }
    };

    return {
        'register': register,
        'display': display
    };
});
