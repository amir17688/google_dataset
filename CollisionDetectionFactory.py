from pyplatformerengine.physics.BasicCollisionDetection import BasicCollisionDetection

"""
     A collision detection decider
"""
class CollisionDetectionFactory:
    _instance  = None
    registered = {}

    """
        Turns new into a singleton retriever.
    """
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CollisionDetectionFactory, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    """
        Registers the new actor into the collision detection.
    """
    def addCollidable(self, actor, entity):
        self.registered[actor] = entity
        actor.collisionDetectionComponent = BasicCollisionDetection()
        
    """
        Initializes the collision detection in the actors.
    """
    def activateCollisionDetection(self):
        allEntities = list(self.registered.values())
        for actor in list(self.registered.keys()):
            actor.collisionDetectionComponent.registerEntities(self.registered[actor], allEntities)