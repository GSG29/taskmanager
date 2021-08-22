# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import os
import boto3

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

#from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to the task keeper skill. You can ask me to keep track of tasks for you and show outstanding tasks. What would you like to do?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ShowTaskIntentHandler(AbstractRequestHandler):
    """Handler for Show Task Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ShowTaskIntent")(handler_input)


    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        try:
            taskLst = attr['tasks']
            speak_output = "Here is what you have in your task list: " 
            for i in range(len(taskLst)):
                speak_output += "task # {} is {},".format( i+1, taskLst[i]) 
        except:
            speak_output = "Your task list is empty - please add something to it"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("What else can I help you with")
                .response
        )

class CreateTaskIntentHandler(AbstractRequestHandler):
    """Handler for Create Task Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CreateTaskIntent")(handler_input)

        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        task = handler_input.request_envelope.request.intent.slots["task_name"].value
        attr_manager = handler_input.attributes_manager
        
        
        try :
            taskLst = attr_manager.persistent_attributes['tasks']
        except:
            taskLst = []
        if task :    
            if str(task) not in taskLst :
                taskLst.append(str(task))
                attr_manager.persistent_attributes = {'tasks' : taskLst}
                attr_manager.save_persistent_attributes() 
                speak_output = "I will add {} to your to do list. You now have {} tasks in your to do list.".format(str(task),str(len(taskLst)))
            else :
                speak_output = " Task {} is already in your to do list. You have {} tasks in your to do list.".format(str(task),str(len(taskLst)))
        else:
            speak_output = "What task should I add to your to do list?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                 .ask("What else can I help you with?")
                .response
        )

class CompleteTaskIntentHandler(AbstractRequestHandler):
    """Handler for Complete Task Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CompleteTaskIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        task =  handler_input.request_envelope.request.intent.slots["task_name"].value
        attr_manager = handler_input.attributes_manager
        
        
        try :
            taskLst = attr_manager.persistent_attributes['tasks']
            if task :    
                if str(task)  in taskLst :
                    taskLst.remove(str(task))
                    attr_manager.persistent_attributes = {'tasks' : taskLst}
                    attr_manager.save_persistent_attributes() 
                    speak_output = "Removed {} from your to do list. You now have {} tasks in your to do list ".format(str(task),str(len(taskLst)))
                else :
                    speak_output = " {} is not in your to do list. You can add it to your to do list".format(str(task))
            else:
                speak_output = "What task should I remove from your to do list?"
        except:
            speak_output = "Your have completed all your tasks.You can add more task to your to do list."

        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        
        
    
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say something like add task cleaning, mark cleaning as done or show me my tasks"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Your task list is empty, please add something to it."
        reprompt = "What else can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


#sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ShowTaskIntentHandler())
sb.add_request_handler(CreateTaskIntentHandler())
sb.add_request_handler(CompleteTaskIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()