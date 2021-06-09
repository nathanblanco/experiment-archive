/*
 * Requires:
 *     psiturk.js
 *     utils.js
 *     constants.js
 */
 
// STUFF FROM OTHER TASK THAT I PROBABLY DONT NEED
 var exp,
 	NROUNDS = 8,
	N_OPTIONS = 4,
	OPTIONS = ['A', 'B', 'C', 'D'],
	OPTION_FADE_OPACITY = 0.3,
	INIT_BONUS = 0,
	BASE_PAYMENT = .5,
	chosen_values = [],
	final_bonus;



// Initalize psiturk object
var psiTurk = new PsiTurk(uniqueId, adServerLoc, mode);
var LOGGING = mode != "debug";

var mycondition = condition;  // 
//console.log(String(condition));
var mycounterbalance = counterbalance;  // 

console.log(mycondition);


if (mycondition%2 === 0) {
	var cond_index = 'G';
	mycondition = "2";
	}
else {
	var cond_index = 'L';
	mycondition = "3";
	}
	
console.log(mycondition);


// Generic function for saving data
function output(arr) {
    psiTurk.recordTrialData(arr);
    if (LOGGING) console.log(arr.join(" "));
};


// All pages to be loaded
var pages = [
	"welcome.html",
	"instructions/instruct-1-G.html",
	"instructions/instruct-1-L.html",
	"instructions/instruct-2-G.html",
	"instructions/instruct-2-L.html",
	"stage.html",
	"postquestionnaire.html",
	"postquestionnaire1.html",
	"postquestionnaire2.html",
	"prequestionnaire.html",
	"carefulcheck.html",
	"cesd.html",
	"adhd.html",
		
];

psiTurk.preloadPages(pages);

var images = [
	"static/images/prechoice.jpg",
	"static/images/chosen.jpg",
	"static/images/not_chosen.jpg",
	"static/images/trial-G2.jpg",
	"static/images/trial-L2.jpg"
];

psiTurk.preloadImages(images);

var welcomeInstructions = [
	"welcome.html"
];
		
var preInstructionPages = [ // add as a list as many pages as you like
	"instructions/instruct-1-"+cond_index+".html",
	//"instructions/instruct-2-"+cond_index+".html",
];



function clear_buttons() {
	$('#buttons').html('');
};


function add_next_button(callback) {

	var label = 'Continue (press \'C\')';
	$('#buttons').append('<button id=btn-next class="btn btn-default btn-lg">'+label+'</button>');

	$(window).bind('keydown', function(e) {
		if (e.keyCode == '67') {
			$(window).unbind('keydown');
			callback();
		};
	});

};  

function add_stop_and_continue_buttons(continue_callback, stop_callback, accept_keypress) {

	var accept_keypress = accept_keypress || true;

	$('#buttons').append('<button id=btn-continue class="btn btn-default btn-info btn-lg">Continue Learning (press \'C\')</button>');
	$('#buttons').append('<button id=btn-stop class="btn btn-default btn-primary btn-lg">Stop and Choose (press \'S\')</button>');

	// if allowing keypresses, set up handlers
	if (accept_keypress) {

		$(window).bind('keydown', function(e) {

			// 'C' for continue
			if (e.keyCode == '67') {
				$(window).unbind('keydown');
				continue_callback();
			};

			// 'S' for stop
			if (e.keyCode == '83') {
				$(window).unbind('keydown');
				stop_callback();
			};
		});

	} else {
		$('#btn-continue').on('click', continue_callback);
		$('#btn-stop').on('click', stop_callback);
	};

};


//
// Option object for displaying urn, sampling outcomes,
// and selecting for final choice
//
var Option = function(stage, id, n_options) {

	var self = this;
	self.id = id;
	self.index = OPTIONS.indexOf(self.id);
	self.stage = stage;

	// work out positioning based on stage size and number of options
	self.row = Math.floor(self.index / 4);
	self.col = self.index % 4;
	self.stage_w = Number(self.stage.attr("width"));
	self.stage_h = Number(self.stage.attr("height"));
	
	switch (n_options) {
		case 1:
			self.x = self.stage_w/2;//350 //
			self.y = 30 + self.stage_h/4;//420 //
			break;
		case 2:
			self.x = 220 + (self.stage_w-140)/2 * self.col;
			self.y = 30 + self.stage_h/4;
			break;
		default:
			self.x = 120 + self.stage_w/4 * self.col;
			self.y = 140 + self.stage_h/2 * self.row;
	};

	self.sample_x = self.x;
	self.sample_y = self.y + 50;

	// state variables
	self.chosen = false;
	self.available = true;
	self.n_opp_samples = 0;

	// drawing of options
	self.disp = self.stage.append('g')
						  .attr('id', self.id)
						  .attr('opacity', 1.);

	self.draw = function() {
		self.obj = self.disp.append('image')
							.attr('x', self.x-100)
							.attr('y', self.y-80)
							.attr('width', 200)
							.attr('height', 200)
							.attr('xlink:href', 'static/images/not_chosen.jpg'); 

		self.label = self.disp.append('text')
							  .attr('x', self.x)
							  .attr('y', self.y+160)
							  .attr('text-anchor', 'middle')
							  .attr('class', 'optionlabel')
							  .attr('stroke', 'black')
							  .text(self.id);

		if (self.chosen) {
			self.highlight();
		} else {

			if (!self.available) {
				self.disp.attr('opacity', OPTION_FADE_OPACITY);
				self.expiration_label = self.stage.append('text')
									.attr('x', self.x)
									.attr('y', self.y+140)
									.attr('class', 'expirationlabel')
									.attr('text-anchor', 'middle')
									.attr('fill', '#DF0101')
									.text('CLAIMED')
									.attr('opacity', 0.);

			};
		};

		return self;
	};

	self.highlight = function() {

        self.chosen = true;

		self.obj.attr('opacity', OPTION_FADE_OPACITY);
		//self.label.attr('opacity', OPTION_FADE_OPACITY);

		self.highlighter = self.disp.append('image')
								    .attr('x', self.x-100)
								    .attr('y', self.y-80)
								    .attr('width', 200)
								    .attr('height', 200)
								    .attr('xlink:href', 'static/images/chosen.jpg');

		self.expiration_label = self.stage.append('text')
							 .attr('x', self.x)
							 .attr('y', self.y+140)
							 .attr('class', 'expirationlabel')
							 .attr('text-anchor', 'middle')
							 .attr('fill', '#E6E6E6')
							 .text('CLAIMED')
							 .attr('opacity', 0.)
							 .transition()
							   .delay(300)
							   .duration(200)
							   .attr('opacity', 0);

		return self;
	};

	self.draw_sample = function(value, loc, duration, backon) {

		loc = loc || [self.sample_x-60, self.sample_y-60];
		backon = backon || false;

		self.coin = self.disp.append('g').attr('id', 'coin');

		self.coin_circle = self.coin.append('circle')
									.attr('r', 50)
									.attr('cx', self.x)
									.attr('cy', self.y)
									.attr('width', 100)
									.attr('height', 100)
									.attr('stroke', 'FFFFFF')
									.attr('stroke-width', 5)
									.attr('fill', '#FFFFFF')
									.transition()
									  .duration(300)
									  .attr('opacity', 1);

		self.coin_label = self.coin.append('text')
				   .attr('x', loc[0]+60)
				   .attr('y', loc[1]+25)
				   .attr('text-anchor', 'middle')
				   .attr('fill', '#000000')
				   .attr('class', 'samplefeedback')
				   .text(value)
				   .attr('opacity', 0)
				   .attr("font-size", "36px")
				   .transition()
				     .duration(300)
					 .attr('opacity', 1);

		if (duration!=undefined) {
			setTimeout(function() {
				self.clear_sample();
				if (backon) self.listen();
			}, duration);
		};

	};
	self.clear_sample = function() {
		if (self.coin != undefined) self.coin.remove();
		if (self.opp_samples != undefined) self.opp_samples.remove();
		self.n_opp_samples = 0;
	};

	self.listen = function(callback) {
		if (callback!=undefined) self.selection_callback = callback;
		self.disp.on('mousedown', function() {
			self.stop_listening();
			if (self.selection_callback!=undefined) self.selection_callback(self.id);
		});
		return self;
	};

	self.click = function() {
		self.selection_callback(self.id);
	};

	self.stop_listening = function() {
		self.disp.on('mousedown', function() {} );
	};

	self.erase = function() {
		self.stage.select(self.id).remove();
	};

	return self;
};
//########################################################################################################


var DiffuseExperiment = function(round, callback, practice) {

	var self = this;
	self.trial = 0; 
	self.response = -1; // initialize response
	self.num_trials = 250;
	self.payoff = 0;
	self.best_option = -1;
	self.n_options = N_OPTIONS;
	//self.gamble = generate_gamble_from_optset(self.round);
	
	
	//self.trialon, // time word is presented
	//    listening = false;

	// main task variables
	// set volatility and valence based on condition	
	if (mycondition === "0") {
		self.volatility = 0; // 0 means low volatility; 1 means high
		self.valence = 1; // 1 means gains; -1 means losses
	}
	else if (mycondition === "1") {
		self.volatility = 0; // 0 means low volatility; 1 means high
		self.valence = -1; // 1 means gains; -1 means losses
	}
	else if (mycondition === "2") {
		self.volatility = 1; // 0 means low volatility; 1 means high
		self.valence = 1; // 1 means gains; -1 means losses
	}
	else if (mycondition === "3") {
		self.volatility = 1; // 0 means low volatility; 1 means high
		self.valence = -1; // 1 means gains; -1 means losses
	}
	else {
	console.log("Error: Invalid condition");
	}
	
	

	// set random-walk diffusion parameters based on volatility 
	if (self.volatility === 0) {
		self.decay = 0.99;
		self.noise = 2.0;
	}
	else {
		self.decay = 0.96;
		self.noise = 4.0;
	}
     
     // set decay center for random walk, and initialize payoff based on valence
     if (self.valence === 1) {
     	self.decay_center = 50;
     	self.payoffs = [Math.floor((Math.random() * 100) + 1),
     				Math.floor((Math.random() * 100) + 1),
     				Math.floor((Math.random() * 100) + 1),
     				Math.floor((Math.random() * 100) + 1)];
     	self.earnings = 0;
     }
     else {
     	self.decay_center = -50;
     	self.payoffs = [Math.floor((Math.random() * -100) ),
     				Math.floor((Math.random() * -100) ),
     				Math.floor((Math.random() * -100) ),
     				Math.floor((Math.random() * -100) )];
     	self.earnings = 15000;
     }
     
     console.log(self.volatility);
	console.log(self.valence);
	console.log(self.decay);
	console.log(self.noise);


	self.reset_stage = function(callback) {
		psiTurk.showPage('stage.html');
		self.stage = d3.select("#stagesvg");
		self.above_stage = d3.select("#aboveStage");
		self.below_stage = d3.select("#belowStage");
		self.instruction = d3.select("#instruction");
		self.disp_turns = d3.select("#disp_turns");
		self.buttons = d3.select("#buttons");
		 self.above_stage.html('<h1>\tTotal points: '+self.earnings+'</h1>'); // 

		self.options = {};
		for (var i=0; i<self.n_options; i++) {
			var opt_label = OPTIONS[i];
			self.options[opt_label] = new Option(self.stage, opt_label, self.n_options);
		};

		callback();
	};


	self.set_instruction = function(text) {
		self.instruction.html('<div id="turn-number">'+text);
	};

	self.set_earnings = function(text) {
		self.disp_turns.html('<div id="disp_turns"> Turn: '+self.trial);
	};


	self.begin = function() {
		self.reset_stage(self.pretrial);
	};

	// ----------------------------------------------------------------------------------
	// main task pretrial: -updates all the payoffs before the trial
	// ----------------------------------------------------------------------------------
	self.pretrial = function() {
		//remove_word();
		if (self.trial === self.num_trials) {
			self.finish();
		}
		else {
	
			
			for (i = 0; i < self.payoffs.length; i++) {
				self.payoffs[i] = self.payoffs[i]*self.decay + (1 - self.decay)*self.decay_center + normal_random(0, Math.pow(self.noise,2));
			}
			
			self.best_option = self.payoffs.indexOf(Math.min.apply(Math, self.payoffs));
			
          	self.sampling_trial();
          }
     };

	self.sampling_trial = function() {
		self.trial += 1;
		//console.log(self.trial);
		// only draw the urns on the first trial
		$.each(self.options, function(i, opt) { opt.draw(); });
				

		var avail = [];
		$.each(self.options, function(i, opt) {
			if (opt.available) {
				avail.push(opt.id);
				opt.listen(self.generate_sample);
			};
		});

		self.set_instruction('Click on a deck to choose a card. Remember, your goal is to have as many points as possible at the end.');
		self.set_earnings();
	};


	self.generate_sample = function(response) {
		
		switch (response) {
		case 'A':
			res=0;
			break;
		case 'B':
			res=1;
			break;
		case 'C':
			res=2;
			break;
		case 'D':
			res=3;
			break;
		};
		
				
		$.each(self.options, function(i, opt) { opt.stop_listening(); });

		self.payoff = Math.floor(self.payoffs[res]);
		
		//console.log(self.payoff);
		
		self.earnings += self.payoff;
			



		psiTurk.recordTrialData({'phase':"MAIN",
                                     'trial': self.trial,
                                     'cond': mycondition,
                                     'volatility': self.volatility,
                                     'valence': self.valence,
                                     'decay': self.decay,
                                     'decay_center': self.decay_center,
                                     'noise': self.noise,
                                     'rew_A': self.payoffs[0],
                                     'rew_B': self.payoffs[1],
                                     'rew_C': self.payoffs[2],
                                     'rew_D': self.payoffs[3],
                                     'response':res, 
                                     'reward': self.payoff, // 
                                     'earnings': self.earnings,
                                     //'hit':hit, // this needs to be determined also
                                     //'rt':rt,
                                     'best_opt': self.best_option}
                                   );


		// show feedback
		self.chosen_id = response;
		self.options[response].chosen = true;
		self.options[response].highlight();
		self.options[response].draw_sample(self.payoff);
		
		
		
		//$.each(self.options, function(i, opt) { opt.clear_sample(); });
		//clear_buttons();

		self.set_instruction('Click on a deck to choose a card. Remember, your goal is to have as many points as possible at the end.');
		self.set_earnings();
		
		setTimeout(function() {
				self.reset_stage(self.pretrial);
			}, 2000);
		

	};


	self.deck_selection = function() {

		// remove any chosen options from the choice set
		$.each(self.options, function(i, opt) { opt.clear_sample(); });
		clear_buttons();

		var make_selection = function(chosen_id) {
			self.chosen_id = chosen_id;
			self.options[chosen_id].chosen = true;
			self.options[chosen_id].highlight();
			self.finish();
		};

		var avail = [];
		$.each(self.options, function(i, opt) {
			avail.push(opt);
			opt.listen(make_selection)
		});
		
	};

	// ---------------------------------------------------------------------------------------------
	// FINISH
	// ---------------------------------------------------------------------------------------------
	self.finish = function() {
	    //$("body").unbind("keydown", response_handler); // Unbind keys
	    currentview = new Questionnaire();
	    // PROBABLY ADD MORE QUESTIONNAIRES HERE 
	};



	self.reset_stage(self.begin);
	return self;
};





// HHHHH****************************************************************************************************************
// QUESTIONNAIRES........................
//**********************************************************************************************************************

/****************
* Questionnaire *
****************/

var Questionnaire = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('postquestionnaire.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	    currentview = new Questionnaire2();
	});
	

    
	
};

/****************
* Questionnaire2 *
****************/

var Questionnaire2 = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire2', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('postquestionnaire1.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire2', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	    currentview = new Questionnaire3();
	});
	

    
	
};

/****************
* Questionnaire3 *
****************/

var Questionnaire3 = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('cesd.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	    currentview = new Questionnaire4();
	});
	
	
};


/****************
* Questionnaire4 *
****************/

var Questionnaire4 = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('carefulcheck.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	    currentview = new Questionnaire5();
	});
	
	
};


/****************
* Questionnaire5 *
****************/

var Questionnaire5 = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('adhd.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire3', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	    currentview = new Questionnaire6();
	});
	
	
};

/****************
* Questionnaire6 *
****************/

var Questionnaire6 = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire4', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
			}
		});

	};

	prompt_resubmit = function() {
		replaceBody(error_message);
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		replaceBody("<h1>Trying to resubmit...</h1>");
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('postquestionnaire2.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire4', 'status':'begin'});
	
	$("#next").click(function () {
	    record_responses();
	    psiTurk.saveData({
            success: function(){
                psiTurk.computeBonus('compute_bonus', function() { 
                	psiTurk.completeHIT(); // when finished saving compute bonus, the quit
                }); 
            }, 
            error: prompt_resubmit});
	});
		
};


/****************
* PreQuestionnaire *
****************/

var PreQuestionnaire = function() {


	var input_list = []; // create an empty array

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'prequestionnaire', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
			
			input_list.push( { age: this.value 
						    });
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);	
			

		});
		$('input').each( function(i, val) {
			if (this.checked == true) {
				psiTurk.recordUnstructuredData(this.name, this.value);		
				

			}
		});
		
		

	};


	
	var do_pre_instructions = function() {
     
     	psiTurk.doInstructions(
    			preInstructionPages,
    			function() { currentview = new DiffuseExperiment(); }
    		);	
     };

	// Load the questionnaire snippet 
	psiTurk.showPage('prequestionnaire.html');
	psiTurk.recordTrialData({'phase':'prequestionnaire', 'status':'begin'});
	
	$("#next").click(function () {
	     record_responses();
	     do_pre_instructions();
	});
	

    
	
};


// Task object to keep track of the current phase
var currentview;

/*******************
 * Run Task
 ******************/
$(window).load( function(){
    psiTurk.doInstructions(
    	welcomeInstructions, // a list of pages you want to display in sequence
    	function() { currentview = new PreQuestionnaire(); } // what you want to do when you are done with instructions
    );
});




