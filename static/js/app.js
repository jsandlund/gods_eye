angular.module('app', [])
  .controller('ctrl', function($scope) {
        $scope.name = "jonny"
  })

  .config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('((');
    $interpolateProvider.endSymbol('))');
  }])
