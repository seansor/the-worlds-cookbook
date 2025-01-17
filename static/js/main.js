function message() {
    $("#delete_message").slideDown();
}

function slide() {
    $("#delete_message").slideUp();
}

function hide() {
    $("#delete_message").fadeOut();
}

$(document).ready(function() {
    
    // select what category to filter ingredients by
    $('#filter-selector ').click(function() {
        $('.card-container').show();
        let filter_option = $('#filter-selector').val();
        if (filter_option == "cuisine") {
            $('#cuisine-selector').show();
            $('#main_ingredient-selector').hide();
        }
        else if (filter_option == "main_ingredient") {
            $('#main_ingredient-selector').show();
            $('#cuisine-selector').hide();
        }
        else {
            $('#main_ingredient-selector').hide();
            $('#cuisine-selector').hide();
            $('.card-container').show();
        }
    });
    
    // select cuisine to filter by
    $('.browse-container').on('click', '#cuisine-selector', function() {
        $('.card-container').show();
        let selected_cuisine = $('#cuisine-selector').val();
        if (selected_cuisine != "all-types") {
            $('.card-container').not('.' + selected_cuisine).hide();
        }
    });
    
    // select main ingredient to filter by
    $('.browse-container').on('click', '#main_ingredient-selector', function() {
        $('.card-container').show();
        let selected_main_ingredient = $('#main_ingredient-selector').val();
        if (selected_main_ingredient != "all-types") {
            $('.card-container').not('.' + selected_main_ingredient).hide();
        }
    });
    
    // add recipe to favourites
    $("#favourite").click(function() {
        $("input[name='favourite']").prop('checked', true);
        $("#favourite-form").submit();
    });
    
    // remove recipe from favourites
    $("#unfavourite").click(function() {
        $("input[name='favourite']").prop('checked', false);
        $("#favourite-form").submit();
    });

    // delete recipe
    $("#delete-recipe").click(function() {
        message();
    });
    
    // cancel delete recipe
    $("#cancel").click(function() {
        slide();
    });
    
    // confrim delete recipe
    $("#confirm-delete").click(function() {
        hide();
    });


    //Add New Cuisine
    $("#cuisine-add").click(function() {
        $("#cuisine").hide()
        $("#cuisine-add").prev('dd').append($("<input type='text' class='form-control' placeholder='Enter Cuisine' value=''></input>")
            .attr("id", "otherCuisine")
            .attr("name", "otherCuisine")
        );
        $("#cuisine-add").hide();
        $("#cuisine-choose").show();
    });

    // show cuisine selector
    $("#cuisine-choose").click(function() {
        $("#otherCuisine").remove();
        $("#cuisine").show();
        $("#cuisine-choose").hide()
        $("#cuisine-add").show();
    });

    //Add Main Ingredient
    $("#main_ingredient-add").click(function() {
        $("#main_ingredient").hide()
        $("#main_ingredient-add").prev('dd').append($("<input type='text' class='form-control' placeholder='Enter Main Ingredient' value=''></input>")
            .attr("id", "otherMain_ingredient")
            .attr("name", "otherMain_ingredient")
        );
        $("#main_ingredient-add").hide();
        $("#main_ingredient-choose").show();
    });

    // Show Main Ingredient selector
    $("#main_ingredient-choose").click(function() {
        $("#otherMain_ingredient").remove();
        $("#main_ingredient").show();
        $("#main_ingredient-choose").hide()
        $("#main_ingredient-add").show();
    });


    //Add ingredient to appropriate ingredient section
    $(".ingredients").on("click", ".addIngredient", function() {
        //split button id to return ingredient list id
        let ingredientListId = this.id.split('-')[0];
        //get number of last ingredient in ingredient section so that appropriate name value can be added
        let lastIngredientNum = parseInt(($("#" + ingredientListId).children('li:last-child').children('input').attr('id')).split('-')[1], 10);
        //get number of selected ingredient section
        let sectionNum_selected = parseInt($("#" + ingredientListId).children('li:last-child').children('input').attr('name').split('s')[1][0], 10);
        if (lastIngredientNum < 20) {
            //append new list element 
            const newListItem = $("<li></li>");
            $("#" + ingredientListId).append(newListItem);
            //append new input element within list element
            if (sectionNum_selected) {
                let newItem = $("<input type='text' value=''></input>")
                    .attr("id", ingredientListId + "-" + (lastIngredientNum + 1))
                    .attr("name", "ingredients" + sectionNum_selected + "-" + (lastIngredientNum + 1));
                $("#" + ingredientListId).children().last().append(newItem);
            }
            else {
                let newItem = $("<input type='text' value=''></input>")
                    .attr("id", ingredientListId + "-" + (lastIngredientNum + 1))
                    .attr("name", "ingredients-" + (lastIngredientNum + 1));
                $("#" + ingredientListId).children().last().append(newItem);
            }
        }
    });

    if ($("label[for='ingredients1']").length) {
        //section_name_1 is defined in script at the end of edit recipe
        //variable passed from app
        $("label[for='ingredients1']").text(section_name_1);
    }

    if ($("label[for='ingredients2']").length) {
        //section_name_2 is defined in script at the end of edit recipe
        //variable passed from app
        $("label[for='ingredients2']").text(section_name_2);
    }

    //Add new ingredient section
    if ($("#ingredients2").length) {
        var sectionNum = 2;
    }
    else if ($("#ingredients1").length) {
        sectionNum = 1;
    }
    else {
        sectionNum = 0;
    }

    //let sectionNum =0;
    $(".ingredients").on("click", "#addIngredientSection", function() {

        //increment section number each time a new section is added so that inputs can be named appropriately
        sectionNum++;

        //create temporary input box and button so that user can add name of new section
        const newSection = $("<input required type='text' class='form-control sectionName' id='sectionName-" + sectionNum + "'name='sectionName-" + sectionNum + "' value='' placeholder='Section Name'></input>");
        const addSection = $("<button type='button' id='addSection'>Add</button>");
        $(".ingredients:last").append(newSection, addSection);

        $("#addIngredientSection").remove();

        if ($("#removeIngredientSection").length) {
            $("#removeIngredientSection").remove();
        }

    });

    //create new ingredient section with name from input box above
    $(".ingredients").on('click', '#addSection', function() {
        //remove add section name dialog once new section added
        $("#sectionName-" + sectionNum).hide();
        $("#addSection").remove();

        //get input for ingredient section name for section title/description tag
        const sectionName = $("#sectionName-" + sectionNum).val();

        //create section id from section name
        const section_id = "ingredients" + sectionNum;

        //create description list elements
        let dt = $("<dt><label for='" + section_id + "'>" + sectionName + "</label>");
        let dd = $("<dd></dd>");
        let ul = $("<ul class='form-control' id='" + section_id + "'></ul>");

        //append description list elements
        $(".ingredients:last").append(dt).append(dd);
        $(".ingredients dd:last").append(ul);

        //create and append list and input elements
        for (let i = 0; i < 3; i++) {
            let li = $("<li></li>");
            let input = $("<input type='text' value=''></input>")
                .attr("id", section_id + "-" + i)
                .attr("name", section_id + "-" + i);
            $(".ingredients ul:last").append(li);
            $(".ingredients ul:last li").each(function() {
                $(this).append(input);
            });
        }

        //create add ingredient button for new section
        const addIngredient = $("<button type='button' class='addItem addIngredient' id='" + section_id + "-add'><div class='button-icon--wrapper'><span class='tooltiptext'>Add Ingredient</span><i class='fa fa-plus' aria-hidden='true'></i></div></button>");
        $(".ingredients").append(addIngredient);

        //add new "add ingredient section" button
        let addIngredientSection = $("<button type='button' class='addItem' id='addIngredientSection'><div class='button-icon--wrapper'><span class='tooltiptext'>Add Ingredient Section</span><i class='fa fa-list-ul' aria-hidden='true'></i><i class='fa fa-plus-circle' aria-hidden='true'></i></div></button>");
        if (sectionNum < 2) {
            $(".ingredients").append(addIngredientSection);
        }
        //add 'remove ingredient section' button
        const removeIngredientSection = $("<button type='button' class='addItem' id='removeIngredientSection'><div class='button-icon--wrapper'><span class='tooltiptext'>Remove Ingredient Section</span><i class='fa fa-list-ul' aria-hidden='true'></i><i class='fa fa-minus-circle' aria-hidden='true'></i></div></button>");
        $(".ingredients").append(removeIngredientSection);


        //return new section number value for use in future iterations of add functions
        return sectionNum;

    });

    $(".ingredients").on('click', '#removeIngredientSection', function() {

        sectionNum--;
        $(this).prev("button").remove();
        $(this).prev("button").remove();
        $(this).prev("dd").remove();
        $(this).prev("dt").remove();
        $(this).prev("input").remove();
        $(this).remove();

        //re-add 'add ingredient section' button to previous section when button doesn't already exist
        if ($("#addIngredientSection").length === 0) {
            let addIngredientSection = $("<button type='button' class='addItem' id='addIngredientSection'><div class='button-icon--wrapper'><span class='tooltiptext'>Add Ingredient Section</span><i class='fa fa-list-ul' aria-hidden='true'></i><i class='fa fa-plus-circle' aria-hidden='true'></i></div></button>");
            $(".ingredients").append(addIngredientSection);
        }

        //add "remove-ingredient-section" button if two sections are still present
        if (sectionNum == 1) {
            const removeIngredientSection = $("<button type='button' class='addItem' id='removeIngredientSection'><div class='button-icon--wrapper'><span class='tooltiptext'>Remove Ingredient Section</span><i class='fa fa-list-ul' aria-hidden='true'></i><i class='fa fa-minus-circle' aria-hidden='true'></i></div></button>");
            $(".ingredients").append(removeIngredientSection);
        }

        return sectionNum;
    });


    let numberSteps = 3;
    // Add new steps to method
    $("#addStep").click(function() {
        if (numberSteps < 10) {
            const newListItem = $("<li></li>");
            let newItem = $("<textarea required type='text' value=''></textarea>")
                .attr("id", "method-" + numberSteps)
                .attr("name", "method-" + numberSteps);
            $("#method").append(newListItem);
            $("#method li:last-child").append(newItem);
            numberSteps++;
            return numberSteps;
        }
        else {
            alert("Please keep method to a maximum of 10 steps");
        }
    });

});
