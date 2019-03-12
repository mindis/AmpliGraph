import tensorflow as tf
import numpy as np
import abc
import logging

REGULARIZER_REGISTRY = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def register_regularizer(name, external_params=[], class_params= {}):
    def insert_in_registry(class_handle):
        REGULARIZER_REGISTRY[name] = class_handle
        class_handle.name = name
        REGULARIZER_REGISTRY[name].external_params = external_params
        REGULARIZER_REGISTRY[name].class_params = class_params
        return class_handle
    return insert_in_registry


class Regularizer(abc.ABC):
    """Abstract class for Regularizer.
    """
    
    name = ""
    external_params = []
    class_params = {}
    
    def __init__(self, hyperparam_dict, verbose=False):
        """Initialize the regularizer.

        Parameters
        ----------
        hyperparam_dict : dict
            dictionary of hyperparams for the regularizer
        """
        self._regularizer_parameters = {}
        
        #perform check to see if all the required external hyperparams are passed
        try:
            self._init_hyperparams(hyperparam_dict)
            if verbose:
                print('------ Regularizer-----')
                logger.info('------ Regularizer-----')
                print('Name:', self.name)
                logger.info('Name:{}'.format(self.name))
                print('Parameters:')
                logger.info('Parameters:')
                for key,value in self._regularizer_parameters.items():
                    logger.info('\t{}:{}\n'.format(key,value))
                    print("  ", key, ": ", value)
            
        except KeyError as e:
            msg = 'Some of the hyperparams for regularizer were not passed.\n{}'.format(e)
            logger.error(msg)
            raise Exception(msg)
            
    def get_state(self, param_name):
        """Get the state value.

        Parameters
        ----------
        param_name : string
            name of the state for which one wants to query the value
        Returns
        -------
        param_value:
            the value of the corresponding state
        """
        try:
            param_value = REGULARIZER_REGISTRY[self.name].class_params.get(param_name)
            return param_value
        except KeyError as e:
            msg = 'Invalid Key.\n{}'.format(e)
            logger.error(msg)
            raise Exception(msg)

    def _init_hyperparams(self, hyperparam_dict):
        """ Verifies and stores the hyperparameters needed by the algorithm.
        
        Parameters
        ----------
        hyperparam_dict : dictionary
            Consists of key value pairs. The regularizer will check the keys to get the corresponding params
        """
        logger.error('This function is a placeholder in an abstract class')
        NotImplementedError("This function is a placeholder in an abstract class")

    def _apply(self, trainable_params):
        """ Apply the regularization function. Every inherited class must implement this function.
        
        (All the TF code must go in this function.)
        
        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized
        
        Returns
        -------
        loss : float
            Regularization Loss
        """
        logger.error('This function is a placeholder in an abstract class')
        NotImplementedError("This function is a placeholder in an abstract class")

    def _inputs_check(self, trainable_params):
        """ Creates any dependencies that need to be checked before performing regularization.
        
        Parameters
        ----------
        trainable_params: list, shape [n]
            List of trainable params that should be reqularized
        """
        pass
        
    def apply(self, trainable_params):
        """ Interface to external world. This function performs input checks, input pre-processing, and
        and applies the loss function.

        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized
        
        Returns
        -------
        loss : float
            Regularization Loss
        """
        self._inputs_check(trainable_params)
        loss = self._apply(trainable_params)
        return loss
    
    
@register_regularizer("None" )      
class NoRegularizer(Regularizer):
    """ Class for performing no regularization.
    """
    
    def __init__(self, hyperparam_dict, verbose=False):
        super().__init__(hyperparam_dict, verbose)
        
    def _init_hyperparams(self, hyperparam_dict):
        """ Verifies and stores the hyperparameters needed by the algorithm.
        
        Parameters
        ----------
        hyperparam_dict : dictionary
            Consists of key value pairs. The regularizer will check the keys to get the corresponding params
        """
        pass
        
        
    def _inputs_check(self, trainable_params):
        """ Creates any dependencies that need to be checked before performing regularization .
        
        Parameters
        ----------
        trainable_params: list, shape [n]
            List of trainable params that should be reqularized
        """
        pass
        
    def _apply(self, trainable_params):
        """ Apply the loss function.

        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized
        
        Returns
        -------
        loss : float
            Regularization Loss

        """
        return tf.constant(0.0)
    
    
@register_regularizer("L1", ['lambda'] )      
class L1Regularizer(Regularizer):
    """Class for performing L1 regularization.
    
    Hyperparameters:
    
    'lambda' - weight for regularizer loss for each parameter(default: 1e-5)
    """
    
    def __init__(self, hyperparam_dict, verbose=False):
        super().__init__(hyperparam_dict, verbose)
        
    def _init_hyperparams(self, hyperparam_dict):
        """ Verifies and stores the hyperparameters needed by the algorithm.
        
        Parameters
        ----------
        hyperparam_dict : dictionary
            Consists of key value pairs. The regularizer will check the keys to get the corresponding params:
            
            'lambda': (list or int)
            
                weight for regularizer loss for each parameter(default: 1e-5). If list, size must be equal to no. of parameters.
        """
        self._regularizer_parameters['lambda'] = hyperparam_dict.get('lambda', 1e-5)
        
        
    def _inputs_check(self, trainable_params):
        """ Creates any dependencies that need to be checked before performing regularization.
        
        Parameters
        ----------
        trainable_params: list, shape [n]
            List of trainable params that should be reqularized
        """
        if np.isscalar(self._regularizer_parameters['lambda']):
            self._regularizer_parameters['lambda'] = [self._regularizer_parameters['lambda']] * len(trainable_params)
        elif isinstance(self._regularizer_parameters['lambda'], list) and len(self._regularizer_parameters['lambda']) == len(trainable_params):
            pass
        else:
            logger.error('Regularizer weight must be a scalar or a list with length equal to number of params passes')
            raise ValueError("Regularizer weight must be a scalar or a list with length equal to number of params passes") 

        
    def _apply(self, trainable_params):
        """ Apply the loss function.

        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized.
        
        Returns
        -------
        loss : float
            Regularization Loss

        """
        loss_reg = 0
        for i in range(len(trainable_params)):
            loss_reg += (self._regularizer_parameters['lambda'][i] * tf.reduce_sum(tf.abs(trainable_params[i])))

        return loss_reg 
    

@register_regularizer("L2", ['lambda'])
class L2Regularizer(Regularizer):
    """Class for performing L2 regularization
    
    Hyperparameters:
    
    'lambda' - weight for regularizer loss for each parameter(default: 1e-5)
    """

    def __init__(self, hyperparam_dict, verbose=False):
        super().__init__(hyperparam_dict, verbose)
        
    def _init_hyperparams(self, hyperparam_dict):
        """ Verifies and stores the hyperparameters needed by the algorithm.
        
        Parameters
        ----------
        hyperparam_dict : dictionary
            Consists of key value pairs. The regularizer will check the keys to get the corresponding params:
            
            'lambda': list or int
            
                weight for regularizer loss for each parameter(default: 1e-5). If list, size must be equal to no. of parameters.
        """
        self._regularizer_parameters['lambda'] = hyperparam_dict.get('lambda', 1e-5)
        
        
    def _inputs_check(self, trainable_params):
        """ Creates any dependencies that need to be checked before performing regularization.
        
        Parameters
        ----------
        trainable_params: list, shape [n]
            List of trainable params that should be reqularized
        """
        if np.isscalar(self._regularizer_parameters['lambda']):
            self._regularizer_parameters['lambda'] = [self._regularizer_parameters['lambda']] * len(trainable_params)
        elif isinstance(self._regularizer_parameters['lambda'], list) and len(self._regularizer_parameters['lambda']) == len(trainable_params):
            pass
        else:
            logger.error('Regularizer weight must be a scalar or a list with length equal to number of params passes')
            raise ValueError("Regularizer weight must be a scalar or a list with length equal to number of params passes") 

        
    def _apply(self, trainable_params):
        """ Apply the loss function.

        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized
        
        Returns
        -------
        loss : float
            Regularization Loss

        """
        loss_reg = 0
        for i in range(len(trainable_params)):
            loss_reg += (self._regularizer_parameters['lambda'][i] * tf.reduce_sum(tf.square(trainable_params[i]))) 

        return loss_reg 
    
@register_regularizer("L3", ['lambda'])
class L3Regularizer(Regularizer):
    """Class for performing L3 regularization
    
    Hyperparameters:
    
    'lambda' - weight for regularizer loss for each parameter(default: 1e-5)
    """

    def __init__(self, hyperparam_dict, verbose=False):
        super().__init__(hyperparam_dict, verbose)
        
    def _init_hyperparams(self, hyperparam_dict):
        """ Verifies and stores the hyperparameters needed by the algorithm.
        
        Parameters
        ----------
        hyperparam_dict : dictionary
            Consists of key value pairs. The regularizer will check the keys to get the corresponding params:
            
            'lambda': list or int
            
                weight for regularizer loss for each parameter(default: 1e-5). If list, size must be equal to no. of parameters.
        """
        self._regularizer_parameters['lambda'] = hyperparam_dict.get('lambda', 1e-5)
        
        
    def _inputs_check(self, trainable_params):
        """ Creates any dependencies that need to be checked before performing regularization.
        
        Parameters
        ----------
        trainable_params: list, shape [n]
            List of trainable params that should be reqularized
        """
        if np.isscalar(self._regularizer_parameters['lambda']):
            self._regularizer_parameters['lambda'] = [self._regularizer_parameters['lambda']] * len(trainable_params)
        elif isinstance(self._regularizer_parameters['lambda'], list) and len(self._regularizer_parameters['lambda']) == len(trainable_params):
            pass
        else:
            logger.error('Regularizer weight must be a scalar or a list with length equal to number of params passes')
            raise ValueError("Regularizer weight must be a scalar or a list with length equal to number of params passes") 

        
    def _apply(self, trainable_params):
        """ Apply the loss function.

        Parameters
        ----------
        trainable_params : list, shape [n]
            List of trainable params that should be reqularized.
        
        Returns
        -------
        loss : float
            Regularization Loss

        """
        loss_reg = 0
        for i in range(len(trainable_params)):
            loss_reg += (self._regularizer_parameters['lambda'][i] * tf.reduce_sum(tf.pow(tf.abs(trainable_params[i]), 3)))

        return loss_reg 
