package com.faceshield.mobile.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.faceshield.mobile.ui.screen.HomeScreen
import com.faceshield.mobile.ui.screen.LoginScreen
import com.faceshield.mobile.ui.screen.PermissionGuideScreen
import com.faceshield.mobile.ui.screen.ResultDetailScreen
import com.faceshield.mobile.ui.screen.SettingsScreen
import com.faceshield.mobile.ui.screen.RecordListScreen

object Routes {
    const val LOGIN = "/login"
    const val PERMISSIONS = "/permissions"
    const val HOME = "/home"
    const val RESULT_DETAIL = "/result/{taskId}"
    const val SETTINGS = "/settings"
    const val RECORDS = "/records"
}

@Composable
fun NavGraph(onRequestMediaProjection: () -> Unit = {}) {
    val navController = rememberNavController()
    val startDestination = Routes.LOGIN

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Routes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Routes.PERMISSIONS) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.PERMISSIONS) {
            PermissionGuideScreen(
                onAllPermissionsGranted = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.PERMISSIONS) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                onNavigateToSettings = { navController.navigate(Routes.SETTINGS) },
                onNavigateToRecords = { navController.navigate(Routes.RECORDS) },
                onNavigateToResult = { taskId ->
                    navController.navigate("/result/$taskId")
                },
                onRequestMediaProjection = onRequestMediaProjection
            )
        }

        composable(
            route = Routes.RESULT_DETAIL,
            arguments = listOf(navArgument("taskId") { type = NavType.IntType })
        ) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getInt("taskId") ?: 0
            ResultDetailScreen(
                taskId = taskId,
                onBack = { navController.popBackStack() }
            )
        }

        composable(Routes.SETTINGS) {
            SettingsScreen(onBack = { navController.popBackStack() })
        }

        composable(Routes.RECORDS) {
            RecordListScreen(
                onBack = { navController.popBackStack() },
                onRecordClick = { taskId ->
                    navController.navigate("/result/$taskId")
                }
            )
        }
    }
}
