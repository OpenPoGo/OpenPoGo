# -*- coding: utf-8 -*-
from app import Plugin
from app import kernel

@kernel.container.register('collect_rewards', ['@api_wrapper', '@event_manager', '@logger'], tags=['plugin'])
class CollectRewards(Plugin):
    """
    # --
    # Plugin: Reward Collector
    # Desription: Will collect level up rewards. It will also print a "level up" notice containing the gained rewards.
    # --
    """
    xp_current = None
    xp_next_level = None
    xp_to_next_level = None
    level_current = None
    level_previous = None

    def __init__(self, api_wrapper, event_manager, logger):
        self.api_wrapper = api_wrapper
        self.event_manager = event_manager
        self.set_logger(logger, 'CollectRewards')

        # register events
        self.event_manager.add_listener('service_player_updated', self.service_player_updated, priority=0)

    def service_player_updated(self, event, data):
        # cancel if no data is provided
        if data == None:
            return

        # get current player info (not calling player, cause that will cause an infinite loop)
        player = data._player

        # store it locally
        CollectRewards.xp_current = int(player.experience)
        CollectRewards.xp_next_level = int(player.next_level_xp)
        CollectRewards.xp_to_next_level = int(player.next_level_xp) - int(player.experience)
        CollectRewards.level_current = int(player.level)

        # check for rewards on startup
        if CollectRewards.level_previous == None:
            # try to claim rewards
            self._claim_levelup_reward()

        # check for level up
        if int(player.level) > CollectRewards.level_current:
            # try to claim rewards
            self._claim_levelup_reward()

        self.log('ServicePlayerUpdated: {} -> ItemCount: {}'.format(CollectRewards.xp_current, data._inventory['count']), color='yellow')

    def _claim_levelup_reward(self):
        # message
        if CollectRewards.level_previous == None:
            CollectRewards.level_previous = CollectRewards.level_current
            self.log('Running initial reward check ...', color='yellow')
        else:
            self.log('Congratulations! You have reached level {}'.format(CollectRewards.level_current), color='green')
