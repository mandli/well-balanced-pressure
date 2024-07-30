subroutine setprob()

    use splitting_module, only: set_splitting
    use energy_module, only: set_energy

    implicit none

    call set_splitting()
    call set_energy()

end subroutine setprob

