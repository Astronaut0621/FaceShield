export const routeNames = {
  login: 'login',
  home: 'home',
  detective: 'detective',
  result: 'result',
  history: 'history',
  historyDetail: 'historyDetail',
  assets: 'assets',
  settings: 'settings'
}

export const navigationItems = [
  { name: routeNames.home, path: '/', label: '首页' },
  { name: routeNames.detective, path: '/detective', label: '图片检测' },
  { name: routeNames.assets, path: '/assets', label: '资产中心' },
  { name: routeNames.history, path: '/history', label: '历史记录' },
  { name: routeNames.settings, path: '/settings', label: '设置' }
]
