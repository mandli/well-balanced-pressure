! Conservation check for specified level.
! This is mostly a debugging tool and assumes grids don't overlap
!
! ******************************************************************
! conck - conservation check  for specified level
!         mostly a debugging tool
!         this assumes grids don't overlap
! 
! ******************************************************************
subroutine conck(level, nvar, naux, time, rest)

    use, intrinsic :: iso_fortran_env, only: real64, real128
    use ieee_arithmetic

    use geoclaw_module, only: rho, g => grav

    use amr_module, only: levelptr, store1, storeaux, ndilo, ndihi, ndjlo, ndjhi
    use amr_module, only: alloc, hxposs, hyposs, possk, lstart, node, nghost, outunit
    use amr_module, only: t0, init_mass, init_KE, init_PE, rnode
    use amr_module, only: cornxlo, cornylo

    use energy_module, only: R_m, press_U => U

    ! Input
    integer, intent(in) :: level, nvar, naux
    real(kind=8), intent(in) :: time
    logical, intent(in) :: rest

    ! Locals
    integer :: mptr, nx, ny, mitot, mjtot
    real(kind=8) :: hx, hy, dt
    real(kind=real128) :: mass, energy, KE, PE, x_low, y_low, x, y, h, u, v

    character(len=100) :: out_form_1 = "('time t = ',e12.5,',  total mass = ',e22.15, '  diff = ',e22.15)"
    character(len=100) :: out_form_2 = "('time t = ',e12.5,',  total KE   = ',e22.15, '  diff = ',e22.15)"
    character(len=100) :: out_form_3 = "('time t = ',e12.5,',  total PE   = ',e22.15, '  diff = ',e22.15)"

    real(kind=real128) :: x_min, y_min, x_max, y_max

    ! Indexing
    iadd(ivar,i,j) = loc + ivar - 1 + nvar * ((j - 1) * mitot + i - 1)
    iaddaux(m,i,j) = locaux + m - 1 + naux * (i - 1) + naux * mitot * (j - 1)

    x_min = ieee_value(x_min, ieee_positive_inf)
    y_min = ieee_value(y_min, ieee_positive_inf)
    x_max = ieee_value(x_max, ieee_negative_inf)
    y_max = ieee_value(y_max, ieee_negative_inf)

    hx      = hxposs(level)
    hy      = hyposs(level)
    dt      = possk(level)
    mass = 0.0_real128
    KE = 0.0_real128
    PE = 0.0_real128

    mptr = lstart(level)
    do while(mptr /= 0)
        loc    = node(store1,mptr)
        locaux = node(storeaux,mptr)
        nx     = node(ndihi,mptr) - node(ndilo,mptr) + 1
        ny     = node(ndjhi,mptr) - node(ndjlo,mptr) + 1
        mitot  = nx + 2*nghost
        mjtot  = ny + 2*nghost
        x_low = rnode(cornxlo,mptr)-nghost*hx
        y_low = rnode(cornylo,mptr)-nghost*hy

        ! print *, nghost * hx, nghost * hy
        ! print *, mptr, x_low, y_low, rnode(cornxlo, mptr), rnode(cornylo, mptr)

        if (mcapa == 0) then
            do j  = nghost+1, mjtot-nghost
                y = y_low + (j - 0.5_real128) * hy
                do i  = nghost+1, mitot-nghost
                    x = x_low + (i - 0.5_real128) * hx
                    if (max(abs(x - press_U * time), abs(y)) <= R_m) then
                        h = alloc(iadd(1,i,j))
                        b = alloc(iaddaux(1,i,j))
                        eta = h + b
                        if (h > 1e-3_real128) then
                            u = alloc(iadd(2,i,j)) / h
                            v = alloc(iadd(3,i,j)) / h
                        else
                            u = 0.0_real128
                            v = 0.0_real128
                        end if

                        mass = mass + h
                        KE = KE + (u**2 + v**2) * h 
                        PE = PE + eta**2
                    else
                        x_min = min(x_min, x)
                        y_min = min(y_min, y)
                        x_max = max(x_max, x)
                        y_max = max(y_max, y)
                    end if
                end do
            end do
        else
            stop "Does not handle capacity..."
        end if

        mptr = node(levelptr,mptr)
    end do
    ! print *, x_min, y_min, x_max, y_max

    mass = mass * rho(1) * hx * hy
    KE = KE * 0.5_real128 * rho(1) * hx * hy
    PE = PE * 0.5_real128 * rho(1) * g * hx * hy

    if (mass < 1d-90) mass = 0.0_real128
    if (KE < 1d-90) KE = 0.0_real128
    if (PE < 1d-90) PE = 0.0_real128

    if (abs(time - t0) < 1e-8 .and. (level == 1) .and. .not. rest) then
        init_mass = mass
        init_KE = KE
        init_PE = PE
        print *, 'Total mass at initial time: ', init_mass
        print *, 'Total E at initial time: ', init_PE + init_KE
    endif

    write(outunit, out_form_1) time, mass, mass - init_mass
    write(outunit, out_form_2) time, KE, KE - init_KE
    write(outunit, out_form_3) time, PE, PE - init_PE

    ! if (abs(totmass - tmass0) > 1d-20) then
    !     print *, "*** mass difference, ", totmass - tmass0,"at t = ", time
    ! end if
end subroutine conck